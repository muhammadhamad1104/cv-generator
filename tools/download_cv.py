"""
Download CV Tool - Retrieves existing CV and returns as base64 for local download
"""

import logging
from typing import Dict, Any
from bson import ObjectId
import base64

from config.database import get_collection
from services.storage_service import StorageService

logger = logging.getLogger(__name__)


class DownloadCVTool:
    """MCP Tool: Download CV as base64"""
    
    def __init__(self):
        self.name = 'download_cv'
        self.description = 'Download an existing CV by ID. Returns PDF as base64 data for local saving.'
        self.input_schema = {
            'type': 'object',
            'properties': {
                'cvId': {
                    'type': 'string',
                    'description': 'The CV ID to download',
                },
            },
            'required': ['cvId'],
        }
        
        self.storage_service = StorageService()
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the CV download tool"""
        cv_id = args.get('cvId')
        
        try:
            logger.info(f"MCP: Downloading CV {cv_id}")
            
            # Get CV record
            cvs_collection = get_collection('cvs')
            cv = await cvs_collection.find_one({'_id': ObjectId(cv_id)})
            
            if not cv:
                return {
                    'success': False,
                    'error': 'CV not found',
                }
            
            # Read PDF file
            import os
            filepath = cv.get('filePath', '')
            
            # Try to read from storage service path
            if not os.path.isabs(filepath):
                full_path = os.path.join(self.storage_service.upload_base_dir, filepath.replace('uploads/', ''))
            else:
                full_path = filepath
            
            if not os.path.exists(full_path):
                return {
                    'success': False,
                    'error': f'CV file not found at: {full_path}',
                }
            
            # Read and encode PDF
            with open(full_path, 'rb') as f:
                pdf_bytes = f.read()
            
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Generate filename
            filename = f"cv_{cv_id}.pdf"
            
            return {
                'success': True,
                'data': {
                    'cvId': str(cv_id),
                    'title': cv.get('title', 'CV'),
                    'template': cv.get('template', 'modern'),
                    'fileSize': len(pdf_bytes),
                    'filename': filename,
                    'pdfBase64': pdf_base64,
                },
                'message': f"CV ready for download: {filename}",
            }
            
        except Exception as error:
            logger.error(f"MCP: Error downloading CV - {str(error)}")
            
            return {
                'success': False,
                'error': 'Failed to download CV',
                'details': str(error),
            }
