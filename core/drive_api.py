"""
Google Drive API wrapper for Hintly.

Handles downloading files from Google Drive.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from core.auth import OAuth2Flow
from core.config import get_config


@dataclass
class DriveFile:
    """Represents a file in Google Drive."""
    
    id: str
    name: str
    mime_type: str
    size: int = 0
    web_view_link: str = ""


class DriveClient:
    """
    Google Drive API client for downloading files.
    
    Used to download PDFs and other materials from Google Classroom.
    """
    
    def __init__(self, credentials: Optional[Credentials] = None):
        """
        Initialize Drive client.
        
        Args:
            credentials: Optional Google credentials. If not provided,
                        will use stored token.
        """
        self.config = get_config()
        
        if credentials is None:
            flow = OAuth2Flow()
            credentials = flow.get_credentials()
            if not credentials:
                raise ValueError("Not authenticated. Run auth.py --setup first.")
        
        self.service = build("drive", "v3", credentials=credentials)
    
    @staticmethod
    def extract_file_id_from_url(url: str) -> str:
        """
        Extract Google Drive file ID from URL.
        
        Args:
            url: Google Drive URL
            
        Returns:
            File ID
            
        Examples:
            >>> DriveClient.extract_file_id_from_url(
            ...     "https://drive.google.com/file/d/1ABC123/view"
            ... )
            '1ABC123'
        """
        # Pattern: /d/{FILE_ID}/ or /d/{FILE_ID}?
        pattern = r"/d/([a-zA-Z0-9_-]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        # Pattern: id={FILE_ID}
        pattern = r"id=([a-zA-Z0-9_-]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        raise ValueError(f"Could not extract file ID from URL: {url}")
    
    def get_file_metadata(self, file_id: str) -> DriveFile:
        """
        Get file metadata from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            DriveFile object with metadata
        """
        file = self.service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, size, webViewLink"
        ).execute()
        
        return DriveFile(
            id=file["id"],
            name=file["name"],
            mime_type=file["mimeType"],
            size=int(file.get("size", 0)),
            web_view_link=file.get("webViewLink", ""),
        )
    
    def download_file(
        self,
        file_id: str,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Download a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            output_path: Optional output path. If not provided,
                        will save to outputs/pdfs/
            
        Returns:
            Path to downloaded file
        """
        # Get file metadata
        metadata = self.get_file_metadata(file_id)
        
        # Determine output path
        if output_path is None:
            output_path = self.config.pdfs_dir / metadata.name
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        request = self.service.files().get_media(fileId=file_id)
        
        with open(output_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        
        return output_path
    
    def download_from_url(
        self,
        url: str,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Download a file from Google Drive URL.
        
        Args:
            url: Google Drive file URL
            output_path: Optional output path
            
        Returns:
            Path to downloaded file
        """
        file_id = self.extract_file_id_from_url(url)
        return self.download_file(file_id, output_path)
