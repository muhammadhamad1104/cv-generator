"""
Profile Management Tools for MCP Server
Provides CRUD operations for user profiles
"""

import logging
from typing import Dict, Any
from bson import ObjectId
from datetime import datetime

from config.database import get_collection

logger = logging.getLogger(__name__)


class GetProfileTool:
    """Get user profile by userId"""
    
    def __init__(self):
        self.name = 'get_profile'
        self.description = 'Retrieve a user profile by userId. Returns complete profile with all sections.'
        self.input_schema = {
            'type': 'object',
            'properties': {
                'userId': {
                    'type': 'string',
                    'description': 'The user ID whose profile to retrieve',
                },
            },
            'required': ['userId'],
        }
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get profile"""
        user_id = args.get('userId')
        
        try:
            profiles_collection = get_collection('profiles')
            profile = await profiles_collection.find_one({'user': ObjectId(user_id)})
            
            if not profile:
                return {
                    'success': False,
                    'error': 'Profile not found. Create a profile first.',
                }
            
            # Convert ObjectId to string for JSON serialization
            profile['_id'] = str(profile['_id'])
            profile['user'] = str(profile['user'])
            
            return {
                'success': True,
                'profile': profile,
            }
            
        except Exception as error:
            logger.error(f"Error getting profile: {str(error)}")
            return {
                'success': False,
                'error': str(error),
            }


class CreateProfileTool:
    """Create a new user profile"""
    
    def __init__(self):
        self.name = 'create_profile'
        self.description = 'Create a new user profile with personal information and sections.'
        self.input_schema = {
            'type': 'object',
            'properties': {
                'userId': {
                    'type': 'string',
                    'description': 'The user ID for the profile',
                },
                'personalInfo': {
                    'type': 'object',
                    'description': 'Personal information',
                    'properties': {
                        'firstName': {'type': 'string'},
                        'lastName': {'type': 'string'},
                        'email': {'type': 'string'},
                        'phone': {'type': 'string'},
                        'address': {'type': 'string'},
                        'city': {'type': 'string'},
                        'country': {'type': 'string'},
                        'postalCode': {'type': 'string'},
                        'dateOfBirth': {'type': 'string'},
                        'nationality': {'type': 'string'},
                        'gender': {'type': 'string'},
                        'profilePhoto': {'type': 'string'},
                    },
                },
                'headline': {'type': 'string', 'description': 'Professional headline'},
                'summary': {'type': 'string', 'description': 'Professional summary'},
                'workExperience': {
                    'type': 'array',
                    'description': 'Work experience entries',
                    'items': {'type': 'object'},
                },
                'education': {
                    'type': 'array',
                    'description': 'Education entries',
                    'items': {'type': 'object'},
                },
                'skills': {
                    'type': 'array',
                    'description': 'Skills list',
                    'items': {'type': 'object'},
                },
                'languages': {
                    'type': 'array',
                    'description': 'Languages list',
                    'items': {'type': 'object'},
                },
                'certifications': {
                    'type': 'array',
                    'description': 'Certifications list',
                    'items': {'type': 'object'},
                },
                'projects': {
                    'type': 'array',
                    'description': 'Projects list',
                    'items': {'type': 'object'},
                },
                'socialLinks': {
                    'type': 'object',
                    'description': 'Social media links',
                    'properties': {
                        'linkedin': {'type': 'string'},
                        'github': {'type': 'string'},
                        'portfolio': {'type': 'string'},
                        'twitter': {'type': 'string'},
                    },
                },
                'hobbies': {
                    'type': 'array',
                    'description': 'Hobbies and interests',
                    'items': {'type': 'string'},
                },
                'references': {
                    'type': 'array',
                    'description': 'Professional references',
                    'items': {'type': 'object'},
                },
            },
            'required': ['userId', 'personalInfo'],
        }
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create profile"""
        user_id = args.get('userId')
        
        try:
            profiles_collection = get_collection('profiles')
            
            # Validate and convert userId to ObjectId
            # If invalid format, generate new ObjectId
            try:
                user_object_id = ObjectId(user_id)
            except:
                # Generate new valid ObjectId if provided ID is invalid
                user_object_id = ObjectId()
                logger.info(f"Generated new ObjectId: {user_object_id} (provided userId was invalid)")
            
            # Check if profile already exists
            existing = await profiles_collection.find_one({'user': user_object_id})
            if existing:
                return {
                    'success': False,
                    'error': 'Profile already exists. Use update_profile instead.',
                }
            
            # Create profile document
            profile_data = {
                'user': user_object_id,
                'personalInfo': args.get('personalInfo', {}),
                'headline': args.get('headline', ''),
                'summary': args.get('summary', ''),
                'workExperience': args.get('workExperience', []),
                'education': args.get('education', []),
                'skills': args.get('skills', []),
                'languages': args.get('languages', []),
                'certifications': args.get('certifications', []),
                'projects': args.get('projects', []),
                'socialLinks': args.get('socialLinks', {}),
                'hobbies': args.get('hobbies', []),
                'references': args.get('references', []),
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
            }
            
            result = await profiles_collection.insert_one(profile_data)
            profile_data['_id'] = str(result.inserted_id)
            profile_data['user'] = str(profile_data['user'])
            
            return {
                'success': True,
                'message': 'Profile created successfully',
                'userId': str(user_object_id),
                'profile': profile_data,
            }
            
        except Exception as error:
            logger.error(f"Error creating profile: {str(error)}")
            return {
                'success': False,
                'error': str(error),
            }


class UpdateProfileTool:
    """Update an existing user profile"""
    
    def __init__(self):
        self.name = 'update_profile'
        self.description = 'Update an existing user profile. Merges provided fields with existing data.'
        self.input_schema = {
            'type': 'object',
            'properties': {
                'userId': {
                    'type': 'string',
                    'description': 'The user ID whose profile to update',
                },
                'personalInfo': {
                    'type': 'object',
                    'description': 'Personal information to update',
                },
                'headline': {'type': 'string'},
                'summary': {'type': 'string'},
                'workExperience': {'type': 'array', 'items': {'type': 'object'}},
                'education': {'type': 'array', 'items': {'type': 'object'}},
                'skills': {'type': 'array', 'items': {'type': 'object'}},
                'languages': {'type': 'array', 'items': {'type': 'object'}},
                'certifications': {'type': 'array', 'items': {'type': 'object'}},
                'projects': {'type': 'array', 'items': {'type': 'object'}},
                'socialLinks': {'type': 'object'},
                'hobbies': {'type': 'array', 'items': {'type': 'string'}},
                'references': {'type': 'array', 'items': {'type': 'object'}},
            },
            'required': ['userId'],
        }
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update profile"""
        user_id = args.get('userId')
        
        try:
            profiles_collection = get_collection('profiles')
            
            # Check if profile exists
            existing = await profiles_collection.find_one({'user': ObjectId(user_id)})
            if not existing:
                return {
                    'success': False,
                    'error': 'Profile not found. Create a profile first.',
                }
            
            # Build update data (exclude userId)
            update_data = {k: v for k, v in args.items() if k != 'userId'}
            update_data['updatedAt'] = datetime.utcnow()
            
            # Update profile
            result = await profiles_collection.update_one(
                {'user': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            # Get updated profile
            profile = await profiles_collection.find_one({'user': ObjectId(user_id)})
            profile['_id'] = str(profile['_id'])
            profile['user'] = str(profile['user'])
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'profile': profile,
            }
            
        except Exception as error:
            logger.error(f"Error updating profile: {str(error)}")
            return {
                'success': False,
                'error': str(error),
            }


class DeleteProfileTool:
    """Delete a user profile"""
    
    def __init__(self):
        self.name = 'delete_profile'
        self.description = 'Delete a user profile completely. This action cannot be undone.'
        self.input_schema = {
            'type': 'object',
            'properties': {
                'userId': {
                    'type': 'string',
                    'description': 'The user ID whose profile to delete',
                },
            },
            'required': ['userId'],
        }
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delete profile"""
        user_id = args.get('userId')
        
        try:
            profiles_collection = get_collection('profiles')
            
            # Check if profile exists
            existing = await profiles_collection.find_one({'user': ObjectId(user_id)})
            if not existing:
                return {
                    'success': False,
                    'error': 'Profile not found.',
                }
            
            # Delete profile
            result = await profiles_collection.delete_one({'user': ObjectId(user_id)})
            
            return {
                'success': True,
                'message': 'Profile deleted successfully',
                'deletedCount': result.deleted_count,
            }
            
        except Exception as error:
            logger.error(f"Error deleting profile: {str(error)}")
            return {
                'success': False,
                'error': str(error),
            }
