"""Read analysis files from Google Drive"""

import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
from src.logger import setup_logger

load_dotenv()

try:
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    from oauth2client.client import OAuth2Credentials
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False
    print("Warning: PyDrive2 not installed. Install with: pip install PyDrive2")

logger = setup_logger()

class DriveReader:
    """Read files from Google Drive folder"""
    
    def __init__(self, folder_id: str):
        """
        Initialize Drive reader
        
        Args:
            folder_id: Google Drive folder ID containing analysis files
        """
        self.folder_id = folder_id
        self.drive = None
        self.enabled = False
        
        if not DRIVE_AVAILABLE:
            logger.error("PyDrive2 not available")
            return
        
        try:
            self._authenticate()
            self.enabled = True
            logger.info(f"✅ Drive reader initialized for folder: {folder_id[:20]}...")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Drive reader: {e}")
            self.enabled = False
    
    def _authenticate(self):
        """Authenticate with Google Drive"""
        refresh_token = os.getenv('GOOGLE_DRIVE_REFRESH_TOKEN', '')
        credentials_file = os.getenv('GOOGLE_DRIVE_CREDENTIALS_FILE', 'credentials.json')
        credentials_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS_JSON', '')
        
        if refresh_token and credentials_json:
            # Create credentials.json from environment variable if needed
            if not os.path.exists(credentials_file):
                try:
                    creds_data = json.loads(credentials_json)
                    with open(credentials_file, 'w') as f:
                        json.dump(creds_data, f)
                    logger.info("Created credentials.json from environment variable")
                except Exception as e:
                    logger.error(f"Failed to create credentials.json: {e}")
                    raise
            
            # Load credentials
            with open(credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            installed = creds_data.get('installed', {})
            client_id = installed.get('client_id') or creds_data.get('client_id')
            client_secret = installed.get('client_secret') or creds_data.get('client_secret')
            
            if client_id and client_secret:
                credentials = OAuth2Credentials(
                    None, client_id, client_secret, refresh_token,
                    None, 'https://oauth2.googleapis.com/token',
                    'Trade Alerts', revoke_uri=None, id_token=None,
                    token_response=None,
                    scopes=['https://www.googleapis.com/auth/drive'],
                    token_info_uri=None
                )
                gauth = GoogleAuth()
                gauth.credentials = credentials
                gauth.Refresh()
                self.drive = GoogleDrive(gauth)
                logger.info("✅ Authenticated with Google Drive")
            else:
                raise ValueError("Missing client_id or client_secret")
        else:
            raise ValueError("GOOGLE_DRIVE_REFRESH_TOKEN and GOOGLE_DRIVE_CREDENTIALS_JSON required")
    
    def list_files(self) -> List[Dict]:
        """
        List all files in the folder
        
        Returns:
            List of file metadata dictionaries
        """
        if not self.enabled or not self.drive:
            logger.error("Drive reader not enabled")
            return []
        
        try:
            file_list = self.drive.ListFile({
                'q': f"'{self.folder_id}' in parents and trashed=false"
            }).GetList()
            
            files = []
            for file in file_list:
                files.append({
                    'id': file['id'],
                    'title': file['title'],
                    'modifiedDate': file['modifiedDate'],
                    'mimeType': file['mimeType']
                })
            
            logger.info(f"Found {len(files)} files in folder")
            return files
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def download_file(self, file_id: str, file_name: str) -> Optional[str]:
        """
        Download a file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            file_name: Local filename to save as
            
        Returns:
            Path to downloaded file, or None if failed
        """
        if not self.enabled or not self.drive:
            return None
        
        try:
            file_drive = self.drive.CreateFile({'id': file_id})
            
            # Create data directory if needed
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            download_path = os.path.join(data_dir, file_name)
            file_drive.GetContentFile(download_path)
            
            logger.info(f"Downloaded {file_name}")
            return download_path
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return None
    
    def get_latest_analysis_files(self, pattern: str = None) -> List[Dict]:
        """
        Get the latest analysis files (sorted by modification date)
        
        Args:
            pattern: Optional filename pattern to filter (e.g., 'summary', 'report')
            
        Returns:
            List of file metadata, sorted by modification date (newest first)
        """
        files = self.list_files()
        
        # Filter by pattern if provided
        if pattern:
            files = [f for f in files if pattern.lower() in f['title'].lower()]
        
        # Sort by modification date (newest first)
        files.sort(key=lambda x: x['modifiedDate'], reverse=True)
        
        return files

