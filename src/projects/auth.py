"""
Authentication System for LabAcc Copilot Multi-User System

Simple username/password authentication with JSON file storage for early development.
Provides user management and authentication verification.
"""

import json
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class User:
    """Represents a user in the system"""
    
    def __init__(self, user_id: str, username: str, password_hash: str, 
                 email: str = "", role: str = "user", created_at: str = None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role  # user, admin
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login: Optional[str] = None
        self.is_active = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create User from dictionary"""
        user = cls(
            user_id=data["user_id"],
            username=data["username"], 
            password_hash=data["password_hash"],
            email=data.get("email", ""),
            role=data.get("role", "user"),
            created_at=data.get("created_at")
        )
        user.last_login = data.get("last_login")
        user.is_active = data.get("is_active", True)
        return user
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches stored hash"""
        return self.password_hash == self._hash_password(password)
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256 (simple for development)"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def set_password(self, password: str):
        """Set user password (hashed)"""
        self.password_hash = self._hash_password(password)

class AuthenticationManager:
    """Manages user authentication and authorization"""
    
    def __init__(self, storage_root: str = "data/"):
        # Future: This will be configurable from a config file
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # User database file
        self.users_file = self.storage_root / "users.json"
        self.users: Dict[str, User] = {}
        
        # Session tokens (in-memory for development)
        self.active_tokens: Dict[str, Dict] = {}
        
        self._load_users()
    
    def _load_users(self):
        """Load users from file"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    for user_data in data.get("users", []):
                        user = User.from_dict(user_data)
                        self.users[user.user_id] = user
                logger.info(f"Loaded {len(self.users)} users")
            except Exception as e:
                logger.error(f"Failed to load users: {e}")
                self.users = {}
        else:
            # Create default users for development
            self._create_default_users()
    
    def _save_users(self):
        """Save users to file"""
        try:
            data = {
                "users": [user.to_dict() for user in self.users.values()],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.users)} users")
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
    
    def _create_default_users(self):
        """Create default users for development"""
        logger.info("Creating default users for development")
        
        # Admin user
        admin_user = User(
            user_id="admin",
            username="admin",
            password_hash=User._hash_password("admin123"),
            email="admin@lab.com",
            role="admin"
        )
        self.users["admin"] = admin_user
        
        # Alice (researcher)
        alice_user = User(
            user_id="alice",
            username="alice",
            password_hash=User._hash_password("alice123"),
            email="alice@lab.com",
            role="user"
        )
        self.users["alice"] = alice_user
        
        # Bob (researcher)  
        bob_user = User(
            user_id="bob",
            username="bob",
            password_hash=User._hash_password("bob123"),
            email="bob@lab.com",
            role="user"
        )
        self.users["bob"] = bob_user
        
        self._save_users()
        
        logger.info("Default users created:")
        logger.info("  admin/admin123 (admin)")
        logger.info("  alice/alice123 (user)")
        logger.info("  bob/bob123 (user)")
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return session token
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Session token if authentication successful, None otherwise
        """
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username and u.is_active:
                user = u
                break
        
        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt for username: {username}")
            return None
        
        # Generate session token
        token = secrets.token_urlsafe(32)
        
        # Store session info
        self.active_tokens[token] = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        # Update last login
        user.last_login = datetime.now().isoformat()
        self._save_users()
        
        logger.info(f"User {username} authenticated successfully")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify session token and return user info
        
        Args:
            token: Session token
            
        Returns:
            User info dict if token valid, None otherwise
        """
        if token not in self.active_tokens:
            return None
        
        session_info = self.active_tokens[token]
        
        # Check if token expired
        expires_at = datetime.fromisoformat(session_info["expires_at"])
        if datetime.now() > expires_at:
            del self.active_tokens[token]
            logger.debug(f"Expired token removed for user {session_info['user_id']}")
            return None
        
        return session_info
    
    def logout(self, token: str) -> bool:
        """Logout user by invalidating token
        
        Args:
            token: Session token to invalidate
            
        Returns:
            True if logout successful
        """
        if token in self.active_tokens:
            user_id = self.active_tokens[token]["user_id"]
            del self.active_tokens[token]
            logger.info(f"User {user_id} logged out")
            return True
        return False
    
    def create_user(self, username: str, password: str, email: str = "", role: str = "user") -> Optional[str]:
        """Create a new user
        
        Args:
            username: Unique username
            password: Password
            email: Optional email
            role: User role (user/admin)
            
        Returns:
            User ID if created successfully, None if username exists
        """
        # Check if username already exists
        for user in self.users.values():
            if user.username == username:
                logger.warning(f"Username {username} already exists")
                return None
        
        # Generate user ID
        user_id = username.lower()
        if user_id in self.users:
            # Add suffix if user_id conflicts
            counter = 1
            while f"{user_id}_{counter}" in self.users:
                counter += 1
            user_id = f"{user_id}_{counter}"
        
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            password_hash=User._hash_password(password),
            email=email,
            role=role
        )
        
        self.users[user_id] = user
        self._save_users()
        
        logger.info(f"Created user {username} with ID {user_id}")
        return user_id
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def list_users(self) -> List[User]:
        """List all users (admin function)"""
        return list(self.users.values())
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user information
        
        Args:
            user_id: User to update
            **kwargs: Fields to update (email, role, is_active)
            
        Returns:
            True if update successful
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Update allowed fields
        if "email" in kwargs:
            user.email = kwargs["email"]
        if "role" in kwargs:
            user.role = kwargs["role"] 
        if "is_active" in kwargs:
            user.is_active = kwargs["is_active"]
        
        self._save_users()
        logger.info(f"Updated user {user_id}")
        return True
    
    def change_password(self, user_id: str, new_password: str) -> bool:
        """Change user password
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.set_password(new_password)
        self._save_users()
        
        logger.info(f"Password changed for user {user_id}")
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user from the system
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if user deleted successfully
        """
        if user_id not in self.users:
            return False
        
        # Remove user from active tokens
        tokens_to_remove = []
        for token, session_info in self.active_tokens.items():
            if session_info["user_id"] == user_id:
                tokens_to_remove.append(token)
        
        for token in tokens_to_remove:
            del self.active_tokens[token]
        
        # Remove user
        username = self.users[user_id].username
        del self.users[user_id]
        self._save_users()
        
        logger.info(f"User {username} (ID: {user_id}) deleted")
        return True
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens"""
        now = datetime.now()
        expired_tokens = []
        
        for token, session_info in self.active_tokens.items():
            expires_at = datetime.fromisoformat(session_info["expires_at"])
            if now > expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.active_tokens[token]
        
        if expired_tokens:
            logger.debug(f"Cleaned up {len(expired_tokens)} expired tokens")

# Global authentication manager instance
auth_manager = AuthenticationManager()