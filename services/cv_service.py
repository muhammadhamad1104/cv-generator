"""
CV Service - Standalone CV generation and validation
Generates PDFs using ReportLab - cloud-compatible, pure Python, no system dependencies
"""

import logging
from typing import Dict, Any, List
import os
from pathlib import Path
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Flowable, HRFlowable
)
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


class CVService:
    """Service for CV operations with ReportLab PDF generation"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / 'templates' / 'cv'
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for CV"""
        # Name/Title style
        self.styles.add(ParagraphStyle(
            name='CVName',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=black,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=white,
            backColor=HexColor('#0066cc'),
            spaceAfter=10,
            spaceBefore=12,
            leftIndent=10,
            rightIndent=10,
            fontName='Helvetica-Bold'
        ))
        
        # Job title / degree style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=black,
            spaceAfter=4,
            fontName='Helvetica-BoldOblique'
        ))
        
        # Company / institution style
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=black,
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))
        
        # Date / meta info style
        self.styles.add(ParagraphStyle(
            name='DateInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=black,
            spaceAfter=4
        ))
        
        # Description style
        self.styles.add(ParagraphStyle(
            name='Description',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=black,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='Contact',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor('#0066cc'),
            spaceAfter=2
        ))
    
    def _format_date(self, date: Any) -> str:
        """Format date helper"""
        if not date or date == 'now':
            return 'Present'
        try:
            d = datetime.fromisoformat(str(date).replace('Z', '+00:00'))
            return f"{d.month}/{d.year}"
        except:
            return str(date)
    
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
        Generate CV PDF using ReportLab
        Cloud-compatible - pure Python, no system dependencies
        """
        try:
            # Prepare data
            data = self._prepare_template_data(profile, settings)
            
            # Create PDF buffer
            pdf_buffer = BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=35*mm,
                leftMargin=35*mm,
                topMargin=25*mm,
                bottomMargin=25*mm
            )
            
            # Build content based on template style
            if template == 'modern':
                story = self._build_modern_template(data)
            elif template == 'classic':
                story = self._build_classic_template(data)
            elif template == 'europass':
                story = self._build_europass_template(data)
            else:
                story = self._build_modern_template(data)  # Default to modern
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            return pdf_bytes
            
        except Exception as error:
            logger.error(f"Error generating CV PDF: {str(error)}")
            raise Exception(f"Failed to generate CV PDF: {str(error)}")
    
    def _build_modern_template(self, data: Dict[str, Any]) -> List:
        """Build modern template layout"""
        story = []
        personal_info = data.get('personalInfo', {})
        
        # Header - Name and Contact
        name = f"{personal_info.get('firstName', '')} {personal_info.get('lastName', '')}".strip()
        if name:
            story.append(Paragraph(name, self.styles['CVName']))
        
        # Contact information
        contact_items = []
        if personal_info.get('email'):
            contact_items.append(f"Email: {personal_info['email']}")
        if personal_info.get('phone'):
            contact_items.append(f"Phone: {personal_info['phone']}")
        if personal_info.get('location'):
            contact_items.append(f"Location: {personal_info['location']}")
        if personal_info.get('linkedin'):
            contact_items.append(f"LinkedIn: {personal_info['linkedin']}")
        
        for contact in contact_items:
            story.append(Paragraph(contact, self.styles['Contact']))
        
        story.append(Spacer(1, 12))
        
        # About Me / Summary
        if data.get('aboutMe'):
            story.append(Paragraph('ABOUT ME', self.styles['SectionHeading']))
            story.append(Paragraph(data['aboutMe'], self.styles['Description']))
            story.append(Spacer(1, 12))
        
        # Work Experience
        work_exp = data.get('workExperience', [])
        if work_exp and data.get('settings', {}).get('sections', {}).get('workExperience', True):
            story.append(Paragraph('WORK EXPERIENCE', self.styles['SectionHeading']))
            for exp in work_exp:
                story.extend(self._build_work_experience(exp))
            story.append(Spacer(1, 12))
        
        # Education
        education = data.get('education', [])
        if education and data.get('settings', {}).get('sections', {}).get('education', True):
            story.append(Paragraph('EDUCATION', self.styles['SectionHeading']))
            for edu in education:
                story.extend(self._build_education(edu))
            story.append(Spacer(1, 12))
        
        # Skills
        skills = data.get('skills', [])
        if skills and data.get('settings', {}).get('sections', {}).get('skills', True):
            story.append(Paragraph('SKILLS', self.styles['SectionHeading']))
            skills_list = [f"{s.get('name', '')} ({s.get('level', '')})" if isinstance(s, dict) else str(s) for s in skills]
            skills_text = ' • '.join(skills_list)
            story.append(Paragraph(skills_text, self.styles['Description']))
            story.append(Spacer(1, 12))
        
        # Projects
        projects = data.get('projects', [])
        if projects and data.get('settings', {}).get('sections', {}).get('projects', True):
            story.append(Paragraph('PROJECTS', self.styles['SectionHeading']))
            for project in projects:
                story.extend(self._build_project(project))
            story.append(Spacer(1, 12))
        
        # Languages
        languages = data.get('languages', [])
        if languages and data.get('settings', {}).get('sections', {}).get('languages', True):
            story.append(Paragraph('LANGUAGES', self.styles['SectionHeading']))
            for lang in languages:
                lang_text = f"<b>{lang.get('language', '')}</b> - {lang.get('proficiency', '')}"
                story.append(Paragraph(lang_text, self.styles['Description']))
            story.append(Spacer(1, 12))
        
        return story
    
    def _build_classic_template(self, data: Dict[str, Any]) -> List:
        """Build classic template layout - Traditional professional style"""
        story = []
        personal_info = data.get('personalInfo', {})
        
        # Header - Name (centered)
        name = f"{personal_info.get('firstName', '')} {personal_info.get('lastName', '')}".strip()
        if name:
            classic_name_style = ParagraphStyle(
                name='ClassicName',
                parent=self.styles['CVName'],
                alignment=TA_CENTER,
                fontSize=22,
                spaceAfter=8
            )
            story.append(Paragraph(name, classic_name_style))
        
        # Contact information (centered)
        contact_parts = []
        if personal_info.get('email'):
            contact_parts.append(personal_info['email'])
        if personal_info.get('phone'):
            contact_parts.append(personal_info['phone'])
        if personal_info.get('location'):
            contact_parts.append(personal_info['location'])
        
        if contact_parts:
            contact_style = ParagraphStyle(
                name='ClassicContact',
                parent=self.styles['Normal'],
                alignment=TA_CENTER,
                fontSize=9,
                spaceAfter=4
            )
            story.append(Paragraph(' | '.join(contact_parts), contact_style))
        
        if personal_info.get('linkedin'):
            story.append(Paragraph(personal_info['linkedin'], contact_style))
        
        story.append(Spacer(1, 16))
        
        # Professional Summary
        if data.get('aboutMe'):
            classic_section_style = ParagraphStyle(
                name='ClassicSection',
                parent=self.styles['Heading2'],
                fontSize=12,
                textColor=black,
                spaceAfter=6,
                spaceBefore=8,
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderColor=black,
                borderPadding=0
            )
            story.append(Paragraph('PROFESSIONAL SUMMARY', classic_section_style))
            story.append(Spacer(1, 2))
            # Add line under section
            story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=8))
            story.append(Paragraph(data['aboutMe'], self.styles['Description']))
            story.append(Spacer(1, 12))
        
        # Work Experience
        work_exp = data.get('workExperience', [])
        if work_exp and data.get('settings', {}).get('sections', {}).get('workExperience', True):
            classic_section_style = ParagraphStyle(
                name='ClassicSection',
                parent=self.styles['Heading2'],
                fontSize=12,
                textColor=black,
                spaceAfter=6,
                spaceBefore=8,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph('PROFESSIONAL EXPERIENCE', classic_section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=8))
            for exp in work_exp:
                story.extend(self._build_work_experience(exp))
            story.append(Spacer(1, 12))
        
        # Education
        education = data.get('education', [])
        if education and data.get('settings', {}).get('sections', {}).get('education', True):
            story.append(Paragraph('EDUCATION', classic_section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=8))
            for edu in education:
                story.extend(self._build_education(edu))
            story.append(Spacer(1, 12))
        
        # Skills
        skills = data.get('skills', [])
        if skills and data.get('settings', {}).get('sections', {}).get('skills', True):
            story.append(Paragraph('SKILLS', classic_section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=8))
            skills_list = [f"{s.get('name', '')} ({s.get('level', '')})" if isinstance(s, dict) else str(s) for s in skills]
            skills_text = ' • '.join(skills_list)
            story.append(Paragraph(skills_text, self.styles['Description']))
            story.append(Spacer(1, 12))
        
        # Languages
        languages = data.get('languages', [])
        if languages and data.get('settings', {}).get('sections', {}).get('languages', True):
            story.append(Paragraph('LANGUAGES', classic_section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=8))
            for lang in languages:
                lang_text = f"<b>{lang.get('language', '')}</b>: {lang.get('proficiency', '')}"
                story.append(Paragraph(lang_text, self.styles['Description']))
            story.append(Spacer(1, 12))
        
        # Projects
        projects = data.get('projects', [])
        if projects and data.get('settings', {}).get('sections', {}).get('projects', True):
            story.append(Paragraph('PROJECTS', classic_section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=8))
            for project in projects:
                story.extend(self._build_project(project))
            story.append(Spacer(1, 12))
        
        return story
    
    def _build_europass_template(self, data: Dict[str, Any]) -> List:
        """Build Europass template layout - EU standard format"""
        story = []
        personal_info = data.get('personalInfo', {})
        
        # Europass header style
        europass_header_style = ParagraphStyle(
            name='EuropassHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#2E5090'),
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        
        europass_section_style = ParagraphStyle(
            name='EuropassSection',
            parent=self.styles['Heading2'],
            fontSize=11,
            textColor=white,
            backColor=HexColor('#2E5090'),
            spaceAfter=8,
            spaceBefore=10,
            leftIndent=8,
            rightIndent=8,
            fontName='Helvetica-Bold'
        )
        
        # Name
        name = f"{personal_info.get('firstName', '')} {personal_info.get('lastName', '')}".strip()
        if name:
            story.append(Paragraph(name, europass_header_style))
        
        # Contact Information Table (Europass format)
        contact_data = []
        if personal_info.get('email'):
            contact_data.append(['Email:', personal_info['email']])
        if personal_info.get('phone'):
            contact_data.append(['Phone:', personal_info['phone']])
        if personal_info.get('location'):
            contact_data.append(['Address:', personal_info['location']])
        if personal_info.get('linkedin'):
            contact_data.append(['LinkedIn:', personal_info['linkedin']])
        
        if contact_data:
            contact_table = Table(contact_data, colWidths=[60, 380])
            contact_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2E5090')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(contact_table)
        
        story.append(Spacer(1, 12))
        
        # Profile / About Me
        if data.get('aboutMe'):
            story.append(Paragraph('PERSONAL STATEMENT', europass_section_style))
            story.append(Paragraph(data['aboutMe'], self.styles['Description']))
            story.append(Spacer(1, 10))
        
        # Work Experience
        work_exp = data.get('workExperience', [])
        if work_exp and data.get('settings', {}).get('sections', {}).get('workExperience', True):
            story.append(Paragraph('WORK EXPERIENCE', europass_section_style))
            for exp in work_exp:
                story.extend(self._build_work_experience(exp))
            story.append(Spacer(1, 10))
        
        # Education and Training
        education = data.get('education', [])
        if education and data.get('settings', {}).get('sections', {}).get('education', True):
            story.append(Paragraph('EDUCATION AND TRAINING', europass_section_style))
            for edu in education:
                story.extend(self._build_education(edu))
            story.append(Spacer(1, 10))
        
        # Personal Skills
        skills = data.get('skills', [])
        languages = data.get('languages', [])
        if (skills or languages) and data.get('settings', {}).get('sections', {}).get('skills', True):
            story.append(Paragraph('PERSONAL SKILLS', europass_section_style))
            
            # Mother tongue / Languages
            if languages:
                for lang in languages:
                    # Check if it's mother tongue
                    is_native = lang.get('proficiency', '').lower() in ['native', 'mother tongue', 'c2']
                    if is_native:
                        story.append(Paragraph(f'<b>Mother tongue:</b> {lang.get("name", "")}', self.styles['Description']))
                    else:
                        # Other languages with CEFR levels
                        lang_name = lang.get('language', '')
                        proficiency = lang.get('proficiency', '')
                        story.append(Paragraph(f'<b>{lang_name}:</b> {proficiency}', self.styles['Description']))
                story.append(Spacer(1, 6))
            
            # Technical/Professional Skills
            if skills:
                story.append(Paragraph('<b>Technical Skills:</b>', self.styles['Description']))
                skills_list = [f"{s.get('name', '')} ({s.get('level', '')})" if isinstance(s, dict) else str(s) for s in skills]
                skills_text = ', '.join(skills_list)
                story.append(Paragraph(skills_text, self.styles['Description']))
            
            story.append(Spacer(1, 10))
        
        # Projects
        projects = data.get('projects', [])
        if projects and data.get('settings', {}).get('sections', {}).get('projects', True):
            story.append(Paragraph('ADDITIONAL INFORMATION', europass_section_style))
            for project in projects:
                story.extend(self._build_project(project))
            story.append(Spacer(1, 10))
        
        return story
    
    def _build_work_experience(self, exp: Dict[str, Any]) -> List:
        """Build work experience section"""
        elements = []
        
        # Job title
        if exp.get('jobTitle'):
            elements.append(Paragraph(exp['jobTitle'], self.styles['JobTitle']))
        
        # Company and dates
        company_info = []
        if exp.get('employer'):
            company_info.append(f"<b>{exp['employer']}</b>")
        
        # Build location from city and country
        location_parts = []
        if exp.get('city'):
            location_parts.append(exp['city'])
        if exp.get('country'):
            location_parts.append(exp['country'])
        if location_parts:
            company_info.append(', '.join(location_parts))
        
        if company_info:
            elements.append(Paragraph(' | '.join(company_info), self.styles['Company']))
        
        # Dates
        start_date = self._format_date(exp.get('startDate'))
        end_date = self._format_date(exp.get('endDate'))
        date_text = f"{start_date} - {end_date}"
        elements.append(Paragraph(date_text, self.styles['DateInfo']))
        
        # Description
        if exp.get('description'):
            elements.append(Paragraph(exp['description'], self.styles['Description']))
        
        elements.append(Spacer(1, 8))
        return elements
    
    def _build_education(self, edu: Dict[str, Any]) -> List:
        """Build education section"""
        elements = []
        
        # Degree
        if edu.get('degree'):
            elements.append(Paragraph(edu['degree'], self.styles['JobTitle']))
        
        # Institution
        if edu.get('institution'):
            elements.append(Paragraph(edu['institution'], self.styles['Company']))
        
        # Dates
        start_date = self._format_date(edu.get('startDate'))
        end_date = self._format_date(edu.get('endDate'))
        date_text = f"{start_date} - {end_date}"
        elements.append(Paragraph(date_text, self.styles['DateInfo']))
        
        # GPA
        if edu.get('gpa'):
            elements.append(Paragraph(f"GPA: {edu['gpa']}", self.styles['DateInfo']))
        
        # Description
        if edu.get('description'):
            elements.append(Paragraph(edu['description'], self.styles['Description']))
        
        elements.append(Spacer(1, 8))
        return elements
    
    def _build_project(self, project: Dict[str, Any]) -> List:
        """Build project section"""
        elements = []
        
        # Project title
        if project.get('title'):
            elements.append(Paragraph(project['title'], self.styles['JobTitle']))
        
        # Technologies
        if project.get('technologies'):
            tech_text = ', '.join(project['technologies']) if isinstance(project['technologies'], list) else project['technologies']
            elements.append(Paragraph(f"<i>{tech_text}</i>", self.styles['DateInfo']))
        
        # Description
        if project.get('description'):
            elements.append(Paragraph(project['description'], self.styles['Description']))
        
        # Links
        if project.get('url'):
            elements.append(Paragraph(f"<a href='{project['url']}'>{project['url']}</a>", self.styles['Contact']))
        
        elements.append(Spacer(1, 8))
        return elements
    
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
