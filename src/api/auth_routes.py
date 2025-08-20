"""
Authentication API Routes for LabAcc Copilot Multi-User System

Provides REST API endpoints for user authentication, login, logout, and user management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List

from src.projects.auth import auth_manager, User
from src.projects.session import session_manager

router = APIRouter(prefix="/api/auth")
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: str
    username: str
    role: str
    message: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str = ""
    role: str = "user"

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    created_at: str
    last_login: Optional[str]
    is_active: bool

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

# Dependency to get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and verify user from bearer token"""
    token = credentials.credentials
    user_info = auth_manager.verify_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info

# Dependency to require admin role
async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role for protected endpoints"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return session token"""
    token = auth_manager.authenticate(request.username, request.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Get user info
    user_info = auth_manager.verify_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication successful but token verification failed"
        )
    
    return LoginResponse(
        token=token,
        user_id=user_info["user_id"],
        username=user_info["username"],
        role=user_info["role"],
        message="Login successful"
    )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user),
                credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user by invalidating token"""
    token = credentials.credentials
    success = auth_manager.logout(token)
    
    if success:
        return {"message": "Logout successful"}
    else:
        return {"message": "Already logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user = auth_manager.get_user(current_user["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
        last_login=user.last_login,
        is_active=user.is_active
    )

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest,
                         current_user: dict = Depends(get_current_user)):
    """Change current user's password"""
    user = auth_manager.get_user(current_user["user_id"])
    
    if not user or not user.check_password(request.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    success = auth_manager.change_password(current_user["user_id"], request.new_password)
    
    if success:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.post("/create-user", response_model=UserResponse)
async def create_user(request: CreateUserRequest,
                     admin_user: dict = Depends(require_admin)):
    """Create a new user (admin only)"""
    user_id = auth_manager.create_user(
        username=request.username,
        password=request.password,
        email=request.email,
        role=request.role
    )
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    user = auth_manager.get_user(user_id)
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
        last_login=user.last_login,
        is_active=user.is_active
    )

@router.get("/users", response_model=List[UserResponse])
async def list_users(admin_user: dict = Depends(require_admin)):
    """List all users (admin only)"""
    users = auth_manager.list_users()
    
    return [
        UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login,
            is_active=user.is_active
        )
        for user in users
    ]

@router.put("/users/{user_id}")
async def update_user(user_id: str,
                     request: UpdateUserRequest,
                     admin_user: dict = Depends(require_admin)):
    """Update user information (admin only)"""
    # Get update fields (only non-None values)
    update_fields = {}
    if request.email is not None:
        update_fields["email"] = request.email
    if request.role is not None:
        update_fields["role"] = request.role
    if request.is_active is not None:
        update_fields["is_active"] = request.is_active
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    success = auth_manager.update_user(user_id, **update_fields)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User {user_id} updated successfully"}

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(user_id: str,
                             new_password: str,
                             admin_user: dict = Depends(require_admin)):
    """Reset user password (admin only)"""
    success = auth_manager.change_password(user_id, new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"Password reset for user {user_id}"}

@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if current token is valid"""
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "role": current_user["role"]
    }

@router.delete("/users/{user_id}")
async def delete_user(user_id: str,
                     admin_user: dict = Depends(require_admin)):
    """Delete a user (admin only)"""
    # Prevent deleting admin user
    user = auth_manager.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin user"
        )
    
    success = auth_manager.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return {"message": f"User {user_id} deleted successfully"}

@router.post("/cleanup")
async def cleanup_expired_tokens(admin_user: dict = Depends(require_admin)):
    """Cleanup expired tokens (admin only)"""
    auth_manager.cleanup_expired_tokens()
    return {"message": "Expired tokens cleaned up"}