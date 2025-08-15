"""
Test utilities for LabAcc Copilot

Provides utilities for multi-user testing, session management,
and backward compatibility with existing test cases.
"""

from .multiuser_test_utils import (
    MultiUserTestManager,
    TestSession,
    ProjectMapping,
    test_manager,
    create_test_session,
    setup_legacy_test_context,
    set_test_session,
    cleanup_test_session,
    get_test_projects
)

__all__ = [
    'MultiUserTestManager',
    'TestSession', 
    'ProjectMapping',
    'test_manager',
    'create_test_session',
    'setup_legacy_test_context',
    'set_test_session',
    'cleanup_test_session',
    'get_test_projects'
]