"""
Storage Service - Handles file storage operations
"""

import os
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageService:
    """Service for file storage operations"""
    
    def __init__(self):
        # Use C:\Downloads\cv-generator for easy access to generated PDFs
        self.upload_base_dir = os.path.join(
            'C:\\',
            'Downloads',
            'cv-generator'
        )
    
    async def save_cv_file(
        self,
        pdf_buffer: bytes,
        user_id: str,
        cv_id: str,
        file_format: str = 'pdf'
    ) -> Dict[str, Any]:
        """Save CV file to storage"""
        try:
            # Create directory structure: uploads/cv/
            cv_dir = os.path.join(self.upload_base_dir, 'cv')
            os.makedirs(cv_dir, exist_ok=True)
            
            # Generate filename: cv_<cvId>_<timestamp>.pdf
            import time
            timestamp = int(time.time() * 1000)
            filename = f"cv_{cv_id}_{timestamp}.{file_format}"
            filepath = os.path.join(cv_dir, filename)
            
            # Write file
            with open(filepath, 'wb') as f:
                f.write(pdf_buffer)
            
            file_size = len(pdf_buffer)
            
            logger.info(f"CV file saved: {filepath} ({file_size} bytes)")
            
            # Return relative path from backend directory
            relative_path = os.path.join('uploads', 'cv', filename)
            
            return {
                'filepath': relative_path,
                'filename': filename,
                'size': file_size,
            }
            
        except Exception as error:
            logger.error(f"Error saving CV file: {str(error)}")
            raise
    
    async def delete_cv_file(self, filepath: str) -> bool:
        """Delete CV file from storage"""
        try:
            full_path = os.path.join(
                os.path.dirname(self.upload_base_dir),
                filepath
            )
            
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"CV file deleted: {full_path}")
                return True
            else:
                logger.warning(f"CV file not found: {full_path}")
                return False
                
        except Exception as error:
            logger.error(f"Error deleting CV file: {str(error)}")
            return False
