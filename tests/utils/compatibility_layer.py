"""
Compatibility Layer for Multi-User Test System

Provides backward compatibility for existing test cases while using
the new multi-user infrastructure underneath. This allows gradual
migration of tests without breaking everything at once.
"""

import asyncio
import logging
from typing import Optional, List
from functools import wraps

from src.agents.react_agent import handle_message as original_handle_message
from .multiuser_test_utils import test_manager, setup_legacy_test_context, set_test_session

logger = logging.getLogger(__name__)

class CompatibilityError(Exception):
    """Raised when compatibility layer encounters issues"""
    pass

async def handle_message_with_compatibility(
    message: str,
    session_id: str = "default",
    current_folder: Optional[str] = None,
    selected_files: Optional[List[str]] = None
) -> str:
    """
    Compatibility wrapper for handle_message that works with old test format.
    
    This function:
    1. Takes old-style parameters (current_folder, selected_files)
    2. Maps them to the new project-based system
    3. Sets up proper session context
    4. Calls the new handle_message function
    5. Returns the response
    
    Args:
        message: User message to process
        session_id: Session identifier for the conversation
        current_folder: Old-style folder reference (e.g., "exp_001_protocol_test")
        selected_files: List of selected files (for context)
        
    Returns:
        Agent response string
        
    Raises:
        CompatibilityError: If setup fails or mapping is not possible
    """
    try:
        # Setup test context from old format
        test_session = await setup_legacy_test_context(
            session_id=session_id,
            current_folder=current_folder,
            selected_files=selected_files
        )
        
        if not test_session:
            raise CompatibilityError(f"Failed to setup test context for folder: {current_folder}")
        
        # Set the current session context
        set_test_session(test_session.session_id)
        
        # If we have a specific folder context, modify the message to include it
        if current_folder and test_session.selected_project:
            # Map old folder reference to project-relative path
            mapping = test_manager.map_old_folder_to_project(current_folder)
            if mapping and mapping.relative_path != ".":
                # Add context about the specific folder within the project
                if not any(folder_ref in message.lower() for folder_ref in ['folder', 'directory', 'exp_']):
                    message = f"In folder {mapping.relative_path}: {message}"
        
        # Add file context if provided
        if selected_files:
            file_context = f" (selected files: {', '.join(selected_files)})"
            message = message + file_context
        
        logger.debug(f"Compatibility layer: mapped '{current_folder}' for session {session_id}")
        logger.debug(f"Final message: {message[:100]}...")
        
        # Call the new handle_message function (no current_folder/selected_files parameters)
        response = await original_handle_message(
            message=message,
            session_id=test_session.session_id
        )
        
        return response
        
    except Exception as e:
        error_msg = f"Compatibility layer error: {str(e)}"
        logger.error(error_msg)
        raise CompatibilityError(error_msg) from e

def create_compatibility_wrapper(handle_message_func):
    """
    Creates a compatibility wrapper for any handle_message function.
    
    This can be used to wrap different versions of handle_message functions
    to ensure they work with the old test format.
    """
    @wraps(handle_message_func)
    async def wrapper(
        message: str,
        session_id: str = "default", 
        current_folder: Optional[str] = None,
        selected_files: Optional[List[str]] = None
    ) -> str:
        return await handle_message_with_compatibility(
            message, session_id, current_folder, selected_files
        )
    
    return wrapper

# Monkey patch for maximum compatibility
# This replaces the import in existing test files automatically
original_import_path = "src.agents.react_agent.handle_message"

def patch_handle_message_imports():
    """
    Monkey patch handle_message imports in test modules for compatibility.
    
    This is a temporary measure to ensure existing tests work without modification.
    """
    import sys
    import importlib
    
    # Store original function
    if 'src.agents.react_agent' in sys.modules:
        module = sys.modules['src.agents.react_agent']
        if not hasattr(module, '_original_handle_message'):
            module._original_handle_message = module.handle_message
            # Replace with compatibility version
            module.handle_message = handle_message_with_compatibility
            logger.info("Patched handle_message for backward compatibility")

def unpatch_handle_message_imports():
    """
    Restore original handle_message function.
    """
    import sys
    
    if 'src.agents.react_agent' in sys.modules:
        module = sys.modules['src.agents.react_agent']
        if hasattr(module, '_original_handle_message'):
            module.handle_message = module._original_handle_message
            delattr(module, '_original_handle_message')
            logger.info("Restored original handle_message")

# Context manager for temporary compatibility
class CompatibilityContext:
    """Context manager for using compatibility mode in tests"""
    
    def __enter__(self):
        patch_handle_message_imports()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        unpatch_handle_message_imports()

def with_compatibility(test_func):
    """Decorator to run a test function with compatibility mode enabled"""
    @wraps(test_func)
    async def wrapper(*args, **kwargs):
        with CompatibilityContext():
            if asyncio.iscoroutinefunction(test_func):
                return await test_func(*args, **kwargs)
            else:
                return test_func(*args, **kwargs)
    return wrapper