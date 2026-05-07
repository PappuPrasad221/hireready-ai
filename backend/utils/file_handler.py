import os
import aiofiles
from fastapi import UploadFile
from datetime import datetime
from typing import Optional
import uuid

class FileHandler:
    def __init__(self):
        self.upload_dir = "uploads"
        self.allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(f"{self.upload_dir}/resumes", exist_ok=True)
        os.makedirs(f"{self.upload_dir}/videos", exist_ok=True)
        os.makedirs(f"{self.upload_dir}/audio", exist_ok=True)
    
    async def save_upload_file(self, file: UploadFile, subfolder: str = "") -> str:
        """Save uploaded file and return file path"""
        try:
            # Validate file
            self._validate_file(file)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create directory path
            if subfolder:
                directory = f"{self.upload_dir}/{subfolder}"
                os.makedirs(directory, exist_ok=True)
                file_path = f"{directory}/{unique_filename}"
            else:
                file_path = f"{self.upload_dir}/{unique_filename}"
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")
    
    def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.allowed_extensions:
            raise Exception(f"File type {file_extension} not allowed")
        
        # Check file size (would need to check content length)
        # This is a simplified check - in production, you'd check actual file size
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': os.path.splitext(file_path)[1].lower()
            }
        except Exception:
            return None
    
    async def cleanup_old_files(self, days_old: int = 30):
        """Clean up files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
            
            return deleted_count
        except Exception:
            return 0
