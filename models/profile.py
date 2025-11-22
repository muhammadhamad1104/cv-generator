"""
Profile Model - User profile schema
Matches backend Profile.js schema exactly
"""

from typing import Optional, List, Dict, Any
from datetime import datetime


class Profile:
    """Profile schema definition for MongoDB operations"""
    
    # Collection name
    COLLECTION = 'profiles'
    
    # Gender options
    GENDER_CHOICES = ['Male', 'Female', 'Other', 'Prefer not to say']
    
    # Skill level options
    SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    
    # Language proficiency options
    LANGUAGE_PROFICIENCY = ['Basic', 'Conversational', 'Fluent', 'Native']
    
    @staticmethod
    def create_schema(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a profile document schema
        Validates and structures data according to backend schema
        """
        schema = {
            'user': data.get('user'),  # ObjectId reference to User
            'personalInfo': {
                'firstName': data.get('personalInfo', {}).get('firstName', ''),
                'lastName': data.get('personalInfo', {}).get('lastName', ''),
                'email': data.get('personalInfo', {}).get('email', ''),
                'phone': data.get('personalInfo', {}).get('phone', ''),
                'address': data.get('personalInfo', {}).get('address', ''),
                'city': data.get('personalInfo', {}).get('city', ''),
                'country': data.get('personalInfo', {}).get('country', ''),
                'postalCode': data.get('personalInfo', {}).get('postalCode', ''),
                'dateOfBirth': data.get('personalInfo', {}).get('dateOfBirth'),
                'nationality': data.get('personalInfo', {}).get('nationality', ''),
                'gender': data.get('personalInfo', {}).get('gender', ''),
                'profilePhoto': data.get('personalInfo', {}).get('profilePhoto', ''),
            },
            'headline': data.get('headline', ''),
            'summary': data.get('summary', ''),
            'workExperience': data.get('workExperience', []),
            'education': data.get('education', []),
            'skills': data.get('skills', []),
            'languages': data.get('languages', []),
            'certifications': data.get('certifications', []),
            'projects': data.get('projects', []),
            'hobbies': data.get('hobbies', []),
            'references': data.get('references', []),
            'socialLinks': {
                'linkedin': data.get('socialLinks', {}).get('linkedin', ''),
                'github': data.get('socialLinks', {}).get('github', ''),
                'twitter': data.get('socialLinks', {}).get('twitter', ''),
                'website': data.get('socialLinks', {}).get('website', ''),
                'portfolio': data.get('socialLinks', {}).get('portfolio', ''),
            },
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
        }
        
        return schema
    
    @staticmethod
    def validate_personal_info(personal_info: Dict[str, Any]) -> List[str]:
        """Validate personal info section"""
        errors = []
        
        if not personal_info.get('firstName'):
            errors.append('First name is required')
        if not personal_info.get('lastName'):
            errors.append('Last name is required')
        if not personal_info.get('email'):
            errors.append('Email is required')
        
        return errors
    
    @staticmethod
    def validate_work_experience(experience: Dict[str, Any]) -> List[str]:
        """Validate work experience entry"""
        errors = []
        
        if not experience.get('jobTitle'):
            errors.append('Job title is required')
        if not experience.get('employer'):
            errors.append('Employer is required')
        if not experience.get('startDate'):
            errors.append('Start date is required')
        
        return errors
    
    @staticmethod
    def validate_education(education: Dict[str, Any]) -> List[str]:
        """Validate education entry"""
        errors = []
        
        if not education.get('institution'):
            errors.append('Institution is required')
        if not education.get('degree'):
            errors.append('Degree is required')
        
        return errors
