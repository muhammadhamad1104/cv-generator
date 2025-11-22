"""
User Model - User authentication schema
Matches backend User.js schema exactly
Note: Password hashing and authentication handled by backend
MCP server only reads user data, doesn't manage authentication
"""

from typing import Optional, Dict, Any
from datetime import datetime


class User:
    """User schema definition for MongoDB operations"""
    
    # Collection name
    COLLECTION = 'users'
    
    @staticmethod
    def create_schema(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a user document schema
        Note: This is primarily for reference
        MCP server doesn't create users - only reads them
        """
        schema = {
            'email': data.get('email', ''),
            'password': data.get('password', ''),  # Should be hashed
            'name': data.get('name', ''),
            'isVerified': data.get('isVerified', False),
            'refreshToken': data.get('refreshToken', ''),
            'resetPasswordToken': data.get('resetPasswordToken'),
            'resetPasswordExpire': data.get('resetPasswordExpire'),
            'lastLogin': data.get('lastLogin'),
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
        }
        
        return schema
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^\S+@\S+\.\S+$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_user_data(user: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from user object"""
        safe_fields = ['_id', 'email', 'name', 'isVerified', 'lastLogin', 'createdAt', 'updatedAt']
        return {k: v for k, v in user.items() if k in safe_fields}
