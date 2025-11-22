"""
Generate CV Tool - Python Implementation
Replicates the functionality of the Node.js generate-cv.js tool
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId

from config.database import get_collection
from services.cv_service import CVService
from services.storage_service import StorageService

logger = logging.getLogger(__name__)


class GenerateCVTool:
    """MCP Tool: Generate CV"""
    
    def __init__(self):
        self.name = 'generate_cv'
        self.description = 'Generate a professional CV from user profile data. Supports Classic, Modern, and Europass templates.'
        self.input_schema = {
            'type': 'object',
            'properties': {
                'userId': {
                    'type': 'string',
                    'description': 'The user ID for whom to generate the CV',
                },
                'cvId': {
                    'type': 'string',
                    'description': 'The CV ID to generate (optional, will create new if not provided)',
                },
                'template': {
                    'type': 'string',
                    'enum': ['classic', 'modern', 'europass'],
                    'description': 'The CV template to use',
                    'default': 'europass',
                },
                'settings': {
                    'type': 'object',
                    'description': 'CV generation settings',
                    'properties': {
                        'color': {'type': 'string', 'default': '#2E5090'},
                        'fontSize': {'type': 'number', 'default': 12},
                        'fontFamily': {'type': 'string', 'default': 'Arial'},
                        'showPhoto': {'type': 'boolean', 'default': True},
                        'sections': {
                            'type': 'object',
                            'properties': {
                                'personalInfo': {'type': 'boolean', 'default': True},
                                'summary': {'type': 'boolean', 'default': True},
                                'workExperience': {'type': 'boolean', 'default': True},
                                'education': {'type': 'boolean', 'default': True},
                                'skills': {'type': 'boolean', 'default': True},
                                'languages': {'type': 'boolean', 'default': True},
                                'certifications': {'type': 'boolean', 'default': True},
                                'projects': {'type': 'boolean', 'default': True},
                                'hobbies': {'type': 'boolean', 'default': False},
                                'references': {'type': 'boolean', 'default': False},
                            },
                        },
                    },
                },
            },
            'required': ['userId'],
        }
        
        self.cv_service = CVService()
        self.storage_service = StorageService()
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the CV generation tool"""
        user_id = args.get('userId')
        cv_id = args.get('cvId')
        template = args.get('template', 'europass')
        settings = args.get('settings', {})
        
        try:
            logger.info(f"MCP: Generating CV for user {user_id}")
            
            # Get collections
            profiles_collection = get_collection('profiles')
            cvs_collection = get_collection('cvs')
            
            # Get user profile
            profile = await profiles_collection.find_one({'user': ObjectId(user_id)})
            if not profile:
                return {
                    'success': False,
                    'error': 'Profile not found. Please create a profile first.',
                }
            
            # Validate CV data
            validation = self.cv_service.validate_cv_data(profile)
            if not validation['isValid']:
                return {
                    'success': False,
                    'error': 'Profile incomplete',
                    'details': validation['errors'],
                }
            
            # Get or create CV record
            cv = None
            if cv_id:
                cv = await cvs_collection.find_one({
                    '_id': ObjectId(cv_id),
                    'user': ObjectId(user_id)
                })
                if not cv:
                    return {
                        'success': False,
                        'error': 'CV not found',
                    }
            else:
                # Create new CV
                cv_doc = {
                    'user': ObjectId(user_id),
                    'profile': profile['_id'],
                    'title': f"CV - {datetime.now().strftime('%m/%d/%Y')}",
                    'template': template,
                    'settings': {
                        **settings,
                        'sections': settings.get('sections', {}),
                    },
                    'status': 'processing',
                    'createdAt': datetime.now(),
                    'updatedAt': datetime.now(),
                }
                result = await cvs_collection.insert_one(cv_doc)
                cv = await cvs_collection.find_one({'_id': result.inserted_id})
            
            # Generate PDF
            pdf_buffer = await self.cv_service.generate_cv(
                profile,
                cv.get('settings', {}),
                cv.get('template', 'europass')
            )
            
            # Save file
            file_info = await self.storage_service.save_cv_file(
                pdf_buffer,
                str(user_id),
                str(cv['_id']),
                'pdf'
            )
            
            # Update CV
            await cvs_collection.update_one(
                {'_id': cv['_id']},
                {
                    '$set': {
                        'filePath': file_info['filepath'],
                        'fileSize': file_info['size'],
                        'status': 'completed',
                        'updatedAt': datetime.now(),
                    }
                }
            )
            
            logger.info(f"MCP: CV generated successfully - {cv['_id']}")
            
            # Get absolute file path
            import os
            absolute_path = os.path.abspath(file_info['filepath'])
            
            return {
                'success': True,
                'data': {
                    'cvId': str(cv['_id']),
                    'title': cv['title'],
                    'template': cv['template'],
                    'status': 'completed',
                    'fileSize': file_info['size'],
                    'filePath': file_info['filepath'],
                    'absolutePath': absolute_path,
                    'createdAt': cv.get('createdAt'),
                },
                'message': f"CV generated successfully! File saved to: {absolute_path}",
            }
            
        except Exception as error:
            logger.error(f"MCP: Error generating CV - {str(error)}")
            
            return {
                'success': False,
                'error': 'Failed to generate CV',
                'details': str(error),
            }
