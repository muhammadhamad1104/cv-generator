"""
CV Service - Standalone CV generation and validation
Generates beautiful PDFs from Handlebars templates - Pure Python implementation
"""

import logging
from typing import Dict, Any, List
import os
from pathlib import Path
from datetime import datetime
from io import BytesIO
import base64
import re

from pybars import Compiler
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.pdfgen import canvas
import html5lib
from xml.etree import ElementTree as ET

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
        Generate CV PDF - renders templates to styled reportlab PDF
        Pure Python, cloud-compatible
        """
        try:
            # Prepare data for template
            data = self._prepare_template_data(profile, settings)
            
            # Generate PDF using reportlab with template styling
            pdf_buffer = BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=15*mm,
                bottomMargin=15*mm
            )
            
            # Build styled content based on template
            story = self._build_template_content(data, template)
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            logger.info(f"Successfully generated {template} CV PDF ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as error:
            logger.error(f"Error generating CV PDF: {str(error)}", exc_info=True)
            raise Exception(f"Failed to generate CV PDF: {str(error)}")
    
    def _build_template_content(self, data: Dict[str, Any], template: str) -> List:
        """Build PDF content with template styling"""
        # Setup custom styles matching template designs
        styles = getSampleStyleSheet()
        
        # Name style - large, bold
        name_style = ParagraphStyle(
            'CVName',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=black,
            spaceAfter=6,
            alignment=TA_LEFT if template == 'modern' else TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Section heading - colored background
        section_style = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=white,
            backColor=HexColor('#0066cc' if template == 'modern' else ('#0054a6' if template == 'classic' else '#2E5090')),
            spaceAfter=10,
            spaceBefore=12,
            leftIndent=10,
            rightIndent=10,
            fontName='Helvetica-Bold'
        )
        
        # Job title style
        job_style = ParagraphStyle(
            'JobTitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=black,
            spaceAfter=4,
            fontName='Helvetica-BoldOblique'
        )
        
        # Company/institution style
        company_style = ParagraphStyle(
            'Company',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            spaceAfter=2,
            fontName='Helvetica-Bold'
        )
        
        # Date style
        date_style = ParagraphStyle(
            'DateInfo',
            parent=styles['Normal'],
            fontSize=9,
            textColor=black,
            spaceAfter=4
        )
        
        # Description style
        desc_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        )
        
        # Contact info style
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#0066cc'),
            spaceAfter=2
        )
        
        story = []
        personal_info = data.get('personalInfo', {})
        
        # Header - Name
        name = f"{personal_info.get('firstName', '')} {personal_info.get('lastName', '')}".strip()
        if name:
            story.append(Paragraph(name, name_style))
        
        # Contact information
        contact_parts = []
        if personal_info.get('email'):
            contact_parts.append(f"<font color='#0066cc'>{personal_info['email']}</font>")
        if personal_info.get('phone'):
            contact_parts.append(personal_info['phone'])
        if personal_info.get('location') or personal_info.get('city'):
            location = personal_info.get('location') or f"{personal_info.get('city', '')}, {personal_info.get('country', '')}".strip(', ')
            contact_parts.append(location)
        
        for contact in contact_parts:
            story.append(Paragraph(contact, contact_style))
        
        story.append(Spacer(1, 12))
        
        # About Me / Summary
        if data.get('summary'):
            story.append(Paragraph('ABOUT ME', section_style))
            story.append(Paragraph(data['summary'], desc_style))
            story.append(Spacer(1, 12))
        
        # Work Experience
        work_exp = data.get('workExperience', [])
        if work_exp and data.get('settings', {}).get('sections', {}).get('workExperience', True):
            story.append(Paragraph('WORK EXPERIENCE', section_style))
            for exp in work_exp:
                if exp.get('jobTitle'):
                    story.append(Paragraph(exp['jobTitle'], job_style))
                
                company_info = []
                if exp.get('employer'):
                    company_info.append(f"<b>{exp['employer']}</b>")
                if exp.get('city') or exp.get('country'):
                    location = f"{exp.get('city', '')}, {exp.get('country', '')}".strip(', ')
                    if location:
                        company_info.append(location)
                
                if company_info:
                    story.append(Paragraph(' | '.join(company_info), company_style))
                
                # Dates
                start_date = self._format_date_helper(None, exp.get('startDate'))
                end_date = 'Present' if exp.get('currentlyWorking') else self._format_date_helper(None, exp.get('endDate'))
                story.append(Paragraph(f"{start_date} - {end_date}", date_style))
                
                if exp.get('description'):
                    story.append(Paragraph(exp['description'], desc_style))
                
                story.append(Spacer(1, 8))
            story.append(Spacer(1, 12))
        
        # Education
        education = data.get('education', [])
        if education and data.get('settings', {}).get('sections', {}).get('education', True):
            story.append(Paragraph('EDUCATION', section_style))
            for edu in education:
                if edu.get('degree'):
                    story.append(Paragraph(edu['degree'], job_style))
                if edu.get('institution'):
                    story.append(Paragraph(edu['institution'], company_style))
                
                start_date = self._format_date_helper(None, edu.get('startDate'))
                end_date = 'Present' if edu.get('currentlyStudying') else self._format_date_helper(None, edu.get('endDate'))
                story.append(Paragraph(f"{start_date} - {end_date}", date_style))
                
                if edu.get('fieldOfStudy'):
                    story.append(Paragraph(f"<i>{edu['fieldOfStudy']}</i>", date_style))
                
                if edu.get('description'):
                    story.append(Paragraph(edu['description'], desc_style))
                
                story.append(Spacer(1, 8))
            story.append(Spacer(1, 12))
        
        # Skills
        skills = data.get('skills', [])
        if skills and data.get('settings', {}).get('sections', {}).get('skills', True):
            story.append(Paragraph('SKILLS', section_style))
            skills_list = []
            for s in skills:
                if isinstance(s, dict):
                    skill_name = s.get('name', '')
                    skill_level = s.get('level', '')
                    if skill_level:
                        skills_list.append(f"{skill_name} ({skill_level})")
                    else:
                        skills_list.append(skill_name)
                else:
                    skills_list.append(str(s))
            skills_text = ' • '.join(skills_list)
            story.append(Paragraph(skills_text, desc_style))
            story.append(Spacer(1, 12))
        
        # Languages
        languages = data.get('languages', [])
        if languages and data.get('settings', {}).get('sections', {}).get('languages', True):
            story.append(Paragraph('LANGUAGES', section_style))
            for lang in languages:
                lang_name = lang.get('language', lang.get('name', ''))
                proficiency = lang.get('proficiency', '')
                story.append(Paragraph(f"<b>{lang_name}</b> - {proficiency}", desc_style))
            story.append(Spacer(1, 12))
        
        # Projects
        projects = data.get('projects', [])
        if projects and data.get('settings', {}).get('sections', {}).get('projects', True):
            story.append(Paragraph('PROJECTS', section_style))
            for project in projects:
                if project.get('title'):
                    story.append(Paragraph(project['title'], job_style))
                if project.get('technologies'):
                    tech = ', '.join(project['technologies']) if isinstance(project['technologies'], list) else project['technologies']
                    story.append(Paragraph(f"<i>{tech}</i>", date_style))
                if project.get('description'):
                    story.append(Paragraph(project['description'], desc_style))
                if project.get('url'):
                    story.append(Paragraph(f"<a href='{project['url']}' color='blue'>{project['url']}</a>", contact_style))
                story.append(Spacer(1, 8))
            story.append(Spacer(1, 12))
        
        return story
    
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
