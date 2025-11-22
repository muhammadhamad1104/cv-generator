"""
CV Model - CV document schema
Matches backend CV.js schema exactly
"""

from typing import Optional, Dict, Any
from datetime import datetime


class CV:
    """CV schema definition for MongoDB operations"""
    
    # Collection name
    COLLECTION = 'cvs'
    
    # Template options
    TEMPLATES = ['europass', 'modern', 'classic', 'minimal']
    
    # Format options
    FORMATS = ['pdf', 'docx']
    
    # Status options
    STATUS_CHOICES = ['draft', 'completed', 'processing', 'failed']
    
    # Default settings
    DEFAULT_SETTINGS = {
        'color': '#2E5090',
        'fontSize': 12,
        'fontFamily': 'Arial',
        'showPhoto': True,
        'sections': {
            'personalInfo': {'enabled': True, 'selectedItems': []},
            'summary': {'enabled': True, 'selectedItems': []},
            'workExperience': {'enabled': True, 'selectedItems': []},
            'education': {'enabled': True, 'selectedItems': []},
            'skills': {'enabled': True, 'selectedItems': []},
            'languages': {'enabled': True, 'selectedItems': []},
            'certifications': {'enabled': True, 'selectedItems': []},
            'projects': {'enabled': True, 'selectedItems': []},
            'hobbies': {'enabled': False, 'selectedItems': []},
            'references': {'enabled': False, 'selectedItems': []},
        },
    }
    
    @staticmethod
    def create_schema(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a CV document schema
        Validates and structures data according to backend schema
        """
        settings = {**CV.DEFAULT_SETTINGS, **data.get('settings', {})}
        
        schema = {
            'user': data.get('user'),  # ObjectId reference to User
            'profile': data.get('profile'),  # ObjectId reference to Profile
            'title': data.get('title', 'My CV'),
            'template': data.get('template', 'europass'),
            'format': data.get('format', 'pdf'),
            'filePath': data.get('filePath', ''),
            'fileUrl': data.get('fileUrl', ''),
            'fileSize': data.get('fileSize', 0),
            'settings': settings,
            'status': data.get('status', 'draft'),
            'downloadCount': data.get('downloadCount', 0),
            'lastDownloaded': data.get('lastDownloaded'),
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
        }
        
        return schema
    
    @staticmethod
    def validate_template(template: str) -> bool:
        """Validate template choice"""
        return template in CV.TEMPLATES
    
    @staticmethod
    def validate_format(format: str) -> bool:
        """Validate format choice"""
        return format in CV.FORMATS
    
    @staticmethod
    def validate_status(status: str) -> bool:
        """Validate status choice"""
        return status in CV.STATUS_CHOICES
    
    @staticmethod
    def merge_settings(existing: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge CV settings with updates"""
        merged = {**existing}
        
        # Update top-level settings
        for key in ['color', 'fontSize', 'fontFamily', 'showPhoto']:
            if key in updates:
                merged[key] = updates[key]
        
        # Merge sections
        if 'sections' in updates:
            merged['sections'] = {**merged.get('sections', {})}
            for section, config in updates['sections'].items():
                if section in merged['sections']:
                    merged['sections'][section] = {**merged['sections'][section], **config}
                else:
                    merged['sections'][section] = config
        
        return merged
