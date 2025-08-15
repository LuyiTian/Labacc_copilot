"""Test cleanup utilities to ensure bob_projects stays clean.

IMPORTANT: All tests that modify bob_projects MUST use these utilities
to ensure the test data is restored to its original state.
"""

import shutil
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class TestCleanup:
    """Manages cleanup of test artifacts in bob_projects."""
    
    def __init__(self, project_root: str = "data/bob_projects"):
        """Initialize cleanup manager.
        
        Args:
            project_root: Path to bob_projects directory
        """
        self.project_root = Path(project_root)
        self.backup_dir = Path("data/bob_projects_backup_20250813_174456")
        self.test_folders: List[Path] = []
    
    def register_test_folder(self, folder_name: str):
        """Register a test folder for cleanup.
        
        Args:
            folder_name: Name of the test folder (e.g., 'exp_test_conversion')
        """
        test_path = self.project_root / folder_name
        self.test_folders.append(test_path)
        logger.info(f"Registered test folder for cleanup: {test_path}")
    
    def cleanup(self) -> bool:
        """Remove all registered test folders.
        
        Returns:
            True if all folders cleaned up successfully
        """
        success = True
        for folder in self.test_folders:
            try:
                if folder.exists():
                    shutil.rmtree(folder)
                    logger.info(f"Removed test folder: {folder}")
            except Exception as e:
                logger.error(f"Failed to remove {folder}: {e}")
                success = False
        
        self.test_folders.clear()
        return success
    
    def restore_from_backup(self) -> bool:
        """Restore entire bob_projects from backup.
        
        This is the nuclear option - completely restores bob_projects
        to its original state from the backup.
        
        Returns:
            True if restoration successful
        """
        if not self.backup_dir.exists():
            logger.error(f"Backup directory not found: {self.backup_dir}")
            return False
        
        try:
            # Remove current bob_projects
            if self.project_root.exists():
                shutil.rmtree(self.project_root)
            
            # Copy from backup
            shutil.copytree(self.backup_dir, self.project_root)
            logger.info(f"Restored bob_projects from backup: {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry - record initial state."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup test folders."""
        self.cleanup()
        return False  # Don't suppress exceptions


def cleanup_test_experiment(experiment_id: str, project_root: str = "data/bob_projects"):
    """Quick function to clean up a single test experiment.
    
    Args:
        experiment_id: ID of the experiment to remove
        project_root: Project root directory
    """
    test_path = Path(project_root) / experiment_id
    if test_path.exists():
        try:
            shutil.rmtree(test_path)
            logger.info(f"Cleaned up test experiment: {experiment_id}")
        except Exception as e:
            logger.error(f"Failed to clean up {experiment_id}: {e}")


def ensure_bob_projects_clean():
    """Ensure bob_projects only contains the original experiments.
    
    This function checks for any folders that weren't in the original
    backup and removes them.
    """
    project_root = Path("data/bob_projects")
    backup_dir = Path("data/bob_projects_backup_20250813_174456")
    
    if not backup_dir.exists():
        logger.warning("Backup directory not found, cannot verify clean state")
        return
    
    # Get list of folders in backup
    backup_folders = {f.name for f in backup_dir.iterdir() if f.is_dir()}
    
    # Get list of current folders
    if project_root.exists():
        current_folders = {f.name for f in project_root.iterdir() if f.is_dir()}
        
        # Find and remove extra folders
        extra_folders = current_folders - backup_folders
        for folder_name in extra_folders:
            folder_path = project_root / folder_name
            try:
                shutil.rmtree(folder_path)
                logger.info(f"Removed extra test folder: {folder_name}")
            except Exception as e:
                logger.error(f"Failed to remove {folder_name}: {e}")
    
    logger.info("bob_projects is clean")


# Usage example in tests:
"""
from src.utils.test_cleanup import TestCleanup

async def test_something():
    with TestCleanup() as cleanup:
        cleanup.register_test_folder("exp_test_001")
        
        # Do your testing here
        # Create exp_test_001 and modify it
        
        # Cleanup happens automatically when exiting the context
"""