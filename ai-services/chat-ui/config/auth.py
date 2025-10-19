"""
Authentication and Authorization for Talentys AI Agent
Secure login system with session management
"""
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# User credentials file
CREDENTIALS_FILE = "config/users.json"

# Session configuration
SESSION_DURATION_HOURS = 8
SESSION_SECRET = os.getenv("SESSION_SECRET", secrets.token_hex(32))

# Default admin credentials (change these!)
DEFAULT_ADMIN = {
    "username": "admin",
    "password_hash": hashlib.sha256("talentys2025".encode()).hexdigest(),  # Default: talentys2025
    "email": "admin@talentys.eu",
    "role": "admin",
    "created_at": datetime.now().isoformat()
}

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> Dict[str, Dict[str, Any]]:
    """Load users from JSON file"""
    if not os.path.exists(CREDENTIALS_FILE):
        # Create default admin user
        users = {"admin": DEFAULT_ADMIN}
        save_users(users)
        return users
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
        return {"admin": DEFAULT_ADMIN}

def save_users(users: Dict[str, Dict[str, Any]]) -> bool:
    """Save users to JSON file"""
    try:
        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user credentials
    Returns user info if successful, None otherwise
    """
    users = load_users()
    
    if username not in users:
        return None
    
    user = users[username]
    password_hash = hash_password(password)
    
    if password_hash == user["password_hash"]:
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        users[username] = user
        save_users(users)
        
        return {
            "username": username,
            "email": user.get("email", ""),
            "role": user.get("role", "user"),
            "last_login": user["last_login"]
        }
    
    return None

def create_user(username: str, password: str, email: str, role: str = "user") -> bool:
    """Create a new user"""
    users = load_users()
    
    if username in users:
        return False
    
    users[username] = {
        "username": username,
        "password_hash": hash_password(password),
        "email": email,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    
    return save_users(users)

def change_password(username: str, old_password: str, new_password: str) -> bool:
    """Change user password"""
    users = load_users()
    
    if username not in users:
        return False
    
    # Verify old password
    if hash_password(old_password) != users[username]["password_hash"]:
        return False
    
    # Update password
    users[username]["password_hash"] = hash_password(new_password)
    users[username]["password_changed_at"] = datetime.now().isoformat()
    
    return save_users(users)

def delete_user(username: str) -> bool:
    """Delete a user (cannot delete admin)"""
    if username == "admin":
        return False
    
    users = load_users()
    
    if username in users:
        del users[username]
        return save_users(users)
    
    return False

def list_users() -> list:
    """List all users (without password hashes)"""
    users = load_users()
    return [
        {
            "username": username,
            "email": user.get("email", ""),
            "role": user.get("role", "user"),
            "created_at": user.get("created_at", ""),
            "last_login": user.get("last_login", "Never")
        }
        for username, user in users.items()
    ]

def is_admin(username: str) -> bool:
    """Check if user is admin"""
    users = load_users()
    return users.get(username, {}).get("role", "user") == "admin"

def create_session_token(username: str) -> str:
    """Create a session token"""
    token_data = f"{username}:{datetime.now().isoformat()}:{secrets.token_hex(16)}"
    return hashlib.sha256(token_data.encode()).hexdigest()

# Initialize users on module import
load_users()
