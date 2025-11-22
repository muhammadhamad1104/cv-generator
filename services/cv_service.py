"""
CV Service - Standalone CV generation and validation
Generates PDFs directly using WeasyPrint - no backend required
"""

import logging
from typing import Dict, Any
import os
from pathlib import Path
from datetime import datetime
from weasyprint import HTML
from pybars import Compiler

logger = logging.getLogger(__name__)


class CVService:
    """Service for CV operations with standalone PDF generation"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / 'templates' / 'cv'
        self.compiler = Compiler()
        self._register_helpers()
    
    def _register_helpers(self):
        """Register Handlebars helpers for template rendering"""
        
        def format_date(this, date):
            """Format date helper"""
            if not date or date == 'now':
                return 'Present'
            try:
                d = datetime.fromisoformat(str(date).replace('Z', '+00:00'))
                return f"{d.month}/{d.year}"
            except:
                return str(date)
        
        def if_equal(this, a, b, options):
            """If equal helper"""
            return options['fn'](this) if a == b else options['inverse'](this)
        
        def join_helper(this, array, separator=', '):
            """Join array helper"""
            if not array:
                return ''
            return separator.join(str(item) for item in array)
        
        # Register helpers with compiler
        self.helpers = {
            'formatDate': format_date,
            'ifEqual': if_equal,
            'join': join_helper,
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
        Generate CV PDF directly using WeasyPrint
        Standalone implementation - no backend required
        """
        try:
            # Load template files
            template_path = self.templates_dir / f'{template}.hbs'
            
            if not template_path.exists():
                raise Exception(f"Template not found: {template}")
            
            # Read template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Prepare template data
            data = self._prepare_template_data(profile, settings)
            
            # Compile and render template
            compiled = self.compiler.compile(template_content)
            html_content = compiled(data, helpers=self.helpers)
            
            # Generate PDF using WeasyPrint
            html = HTML(string=html_content)
            pdf_bytes = html.write_pdf()
            
            return pdf_bytes
            
        except Exception as error:
            logger.error(f"Error generating CV PDF: {str(error)}")
            raise Exception(f"Failed to generate CV PDF: {str(error)}")
    
    def _prepare_template_data(self, profile: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        data = {**profile}
        data['settings'] = settings
        
        # Filter sections based on settings
        if settings.get('sections'):
            for section, enabled in settings['sections'].items():
                if not enabled:
                    data[section] = None
        
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
            else:
                return obj
        
        return convert_objectid(profile)
