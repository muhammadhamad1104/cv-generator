"""
CV Service - Standalone CV generation and validation
Generates beautiful PDFs from Handlebars templates using xhtml2pdf
"""

import logging
from typing import Dict, Any, List
import os
from pathlib import Path
from datetime import datetime
from io import BytesIO
import base64

from pybars import Compiler
from xhtml2pdf import pisa

logger = logging.getLogger(__name__)


class CVService:
    """Service for CV operations with Handlebars template rendering"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / 'templates' / 'cv'
        self.compiler = Compiler()
    
    def _format_date_helper(self, this, date):
        """Handlebars helper for date formatting"""
        if not date or date == 'now':
            return 'Present'
        try:
            if isinstance(date, str):
                d = datetime.fromisoformat(date.replace('Z', '+00:00'))
            elif isinstance(date, datetime):
                d = date
            else:
                return str(date)
            return f"{d.strftime('%m/%Y')}"
        except:
            return str(date) if date else ''
    
    def _get_helpers(self):
        """Get Handlebars helper functions"""
        return {
            'formatDate': self._format_date_helper
        }
    
    def validate_cv_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate CV data completeness"""
        errors = []
        
        # Check personal info
        if not profile.get('personalInfo'):
            errors.append('Personal information is required')
        else:
            personal_info = profile['personalInfo']
            if not personal_info.get('firstName'):
                errors.append('First name is required')
            if not personal_info.get('lastName'):
                errors.append('Last name is required')
            if not personal_info.get('email'):
                errors.append('Email is required')
        
        # Check if at least one section has content
        has_content = False
        sections = ['workExperience', 'education', 'skills', 'projects']
        for section in sections:
            if profile.get(section) and len(profile[section]) > 0:
                has_content = True
                break
        
        if not has_content:
            errors.append('At least one section (work experience, education, skills, or projects) must have content')
        
        return {
            'isValid': len(errors) == 0,
            'errors': errors,
        }
    
    async def generate_cv(
        self,
        profile: Dict[str, Any],
        settings: Dict[str, Any],
        template: str
    ) -> bytes:
        """
        Generate CV PDF using Handlebars templates and xhtml2pdf
        Renders beautiful HTML/CSS templates to PDF (cloud-compatible, pure Python)
        """
        try:
            # Prepare data for template
            data = self._prepare_template_data(profile, settings)
            
            # Load template file
            template_file = self.templates_dir / f"{template}.hbs"
            if not template_file.exists():
                logger.warning(f"Template {template} not found, using classic")
                template_file = self.templates_dir / "classic.hbs"
            
            # Read template
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Compile template
            compiled_template = self.compiler.compile(template_content)
            
            # Render with data and helpers
            html_content = compiled_template(data, helpers=self._get_helpers())
            
            # Generate PDF from HTML using xhtml2pdf
            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_buffer,
                encoding='utf-8'
            )
            
            if pisa_status.err:
                raise Exception(f"PDF generation failed with errors")
            
            # Get PDF bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            logger.info(f"Successfully generated {template} CV PDF ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as error:
            logger.error(f"Error generating CV PDF: {str(error)}", exc_info=True)
            raise Exception(f"Failed to generate CV PDF: {str(error)}")
    
    def _prepare_template_data(self, profile: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        # Serialize profile (convert ObjectId to string)
        serialized_profile = self._serialize_profile(profile)
        
        # Merge settings with defaults
        default_settings = {
            'showPhoto': settings.get('showPhoto', True),
            'color': settings.get('color', '#2E5090'),
            'fontSize': settings.get('fontSize', 12),
            'fontFamily': settings.get('fontFamily', 'Arial'),
            'sections': {
                'personalInfo': True,
                'summary': True,
                'workExperience': True,
                'education': True,
                'skills': True,
                'languages': True,
                'certifications': True,
                'projects': True,
                'hobbies': False,
                'references': False,
            }
        }
        
        # Merge user settings
        if settings.get('sections'):
            default_settings['sections'].update(settings['sections'])
        
        # Prepare template data
        data = {
            **serialized_profile,
            'settings': default_settings
        }
        
        # Ensure socialLinks exists
        if 'socialLinks' not in data:
            data['socialLinks'] = {}
        
        # Move LinkedIn to socialLinks if in personalInfo
        if data.get('personalInfo', {}).get('linkedin'):
            data['socialLinks']['linkedin'] = data['personalInfo']['linkedin']
        
        return data
    
    def _serialize_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize profile data (convert ObjectId to string)"""
        from bson import ObjectId
        
        def convert_objectid(obj):
            if isinstance(obj, dict):
                return {k: convert_objectid(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_objectid(item) for item in obj]
            elif isinstance(obj, ObjectId):
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj
        
        return convert_objectid(profile)
