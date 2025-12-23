#!/usr/bin/env python3
"""
Auto-cleanup service for deleting temporary files after 5 minutes.
Since OSS lifecycle minimum is 1 day, we implement app-level cleanup.
"""

import asyncio

import os
import uuid
import io
import requests
from datetime import datetime, timedelta
from typing import Dict
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from fastapi import UploadFile

from src.exceptions import GeneralErrorExcpetion
from src.ossConfig import get_oss

from src.crypto.services import decrypt_file_from_oss
from src.loggerServices import log_error


@dataclass
class TempFile:
    """Temporary file tracking information."""
    object_name: str
    created_at: datetime
    download_url: str
    cleanup_scheduled: bool = False

class AutoCleanupService:
    """
    Service for automatic cleanup of temporary files after specified minutes.
    """
    
    def __init__(self, cleanup_minutes: int = 5):
        self.cleanup_minutes = cleanup_minutes
        self.temp_files: Dict[str, TempFile] = {}
        self.oss_client = get_oss()
        self.cleanup_tasks: Dict[str, asyncio.Task] = {}
        
    async def register_temp_file(self, object_name: str, download_url: str) -> str:
        """
        Register a temporary file for automatic cleanup.
        
        Args:
            object_name: OSS object name
            download_url: Download URL for the file
            
        Returns:
            temp_id: Unique ID for tracking this file
        """
        temp_id = uuid.uuid4().hex
        temp_file = TempFile(
            object_name=object_name,
            created_at=datetime.now(ZoneInfo("Asia/Hong_Kong")),
            download_url=download_url
        )
        
        self.temp_files[temp_id] = temp_file
        
        # Schedule cleanup after specified minutes
        cleanup_task = asyncio.create_task(
            self._schedule_cleanup(temp_id, self.cleanup_minutes * 60)
        )
        self.cleanup_tasks[temp_id] = cleanup_task
        
        # log_info(f"Registered temp file for cleanup: {object_name} (cleanup in {self.cleanup_minutes} minutes)")
        return temp_id
    
    async def _schedule_cleanup(self, temp_id: str, delay_seconds: int):
        """
        Schedule cleanup of a specific file after delay.
        """
        try:
            # log_info(f"Scheduling cleanup for {temp_id} in {delay_seconds} seconds")
            await asyncio.sleep(delay_seconds)
            
            if temp_id in self.temp_files:
                await self._cleanup_file(temp_id)
            
        except asyncio.CancelledError:
            log_error(f"Cleanup cancelled for {temp_id}")
        except Exception as e:
            log_error(f"Cleanup scheduling failed for {temp_id}: {e}")
    
    async def _cleanup_file(self, temp_id: str):
        """
        Clean up a specific temporary file.
        """
        try:
            if temp_id not in self.temp_files:
                return
            
            temp_file = self.temp_files[temp_id]
            object_name = temp_file.object_name
            
            # Delete from OSS
            success = self.oss_client.delete_file(object_name)
            
            if success:
                # Remove from tracking
                del self.temp_files[temp_id]
                if temp_id in self.cleanup_tasks:
                    del self.cleanup_tasks[temp_id]
                
                age_minutes = (datetime.now(ZoneInfo("Asia/Hong_Kong")) - temp_file.created_at).total_seconds() / 60
                # log_info(f"Cleaned up temp file: {object_name} (age: {age_minutes:.1f} minutes)")
            else:
                log_error(f"Failed to delete temp file: {object_name}")
                
        except Exception as e:
            log_error(f"Cleanup failed for {temp_id}: {e}")
    
    async def cleanup_expired_files(self):
        """
        Manually clean up all expired files (backup cleanup).
        """
        current_time = datetime.now(ZoneInfo("Asia/Hong_Kong"))
        expired_files = []
        
        for temp_id, temp_file in self.temp_files.items():
            age = current_time - temp_file.created_at
            if age > timedelta(minutes=self.cleanup_minutes):
                expired_files.append(temp_id)
        
        for temp_id in expired_files:
            await self._cleanup_file(temp_id)
        
        # log_info(f"Manual cleanup completed: {len(expired_files)} files cleaned")
        return len(expired_files)
    
    def get_stats(self) -> dict:
        """
        Get statistics about temporary files.
        """
        current_time = datetime.now(ZoneInfo("Asia/Hong_Kong"))
        stats = {
            'total_files': len(self.temp_files),
            'cleanup_minutes': self.cleanup_minutes,
            'files_by_age': {
                'under_1min': 0,
                '1_to_3min': 0,
                '3_to_5min': 0,
                'over_5min': 0
            },
            'scheduled_cleanups': len(self.cleanup_tasks)
        }
        
        for temp_file in self.temp_files.values():
            age_minutes = (current_time - temp_file.created_at).total_seconds() / 60
            
            if age_minutes < 1:
                stats['files_by_age']['under_1min'] += 1
            elif age_minutes < 3:
                stats['files_by_age']['1_to_3min'] += 1
            elif age_minutes < 5:
                stats['files_by_age']['3_to_5min'] += 1
            else:
                stats['files_by_age']['over_5min'] += 1
        
        return stats
    
    async def force_cleanup_all(self):
        """
        Force cleanup of all temporary files immediately.
        """
        temp_ids = list(self.temp_files.keys())
        
        # Cancel all scheduled tasks
        for task in self.cleanup_tasks.values():
            task.cancel()
        
        # Clean up all files
        for temp_id in temp_ids:
            await self._cleanup_file(temp_id)
        
        # log_info(f"Force cleanup completed: {len(temp_ids)} files cleaned")
        return len(temp_ids)

# Global service instance
auto_cleanup_service = AutoCleanupService(cleanup_minutes=5)

# Enhanced download function with 5-minute cleanup
async def download_with_5min_cleanup(filename: str, expiration: int = 3600) -> str:
    """
    Download and decrypt file with 5-minute automatic cleanup.
    """
    try:
        # log_info(f"Starting decryption for {filename}")
        
        # Step 1: Download and decrypt
        enc_path = filename if filename.endswith('.enc') else filename + '.enc'
        key_path = enc_path.replace('.enc', '.key')
        
        oss_client = get_oss()
        url_enc = oss_client.download_file(enc_path, expiration)
        url_key = oss_client.download_file(key_path, expiration)
        
        # log_info(f"Downloading encrypted file from: {url_enc[:50]}...")
        # log_info(f"Downloading key file from: {url_key[:50]}...")
        
        response_enc = requests.get(url_enc)
        response_enc.raise_for_status()
        response_key = requests.get(url_key)
        response_key.raise_for_status()
        
        # log_info(f"Encrypted file size: {len(response_enc.content)} bytes")
        # log_info(f"Key file response size: {len(response_key.content)} bytes")
        
        # Improved key content decoding with better consistency and logging
        key_content = None
        decoding_method = None
        
        # Method 1: Try direct content decode (most reliable for text files)
        try:
            key_content = response_key.content.decode('utf-8').strip()
            decoding_method = "content.decode('utf-8')"
            # log_info(f" Key decoded using method: {decoding_method}")
        except UnicodeDecodeError as e:
            log_error(f"UTF-8 decode failed: {e}")
            
            # Method 2: Try response.text (handles encoding automatically)
            try:
                key_content = response_key.text.strip()
                decoding_method = "response.text"
                # log_info(f" Key decoded using method: {decoding_method}")
            except Exception as e:
                log_error(f"response.text failed: {e}")
                
                # Method 3: Last resort with error handling
                try:
                    key_content = response_key.content.decode('utf-8', errors='replace').strip()
                    decoding_method = "content.decode('utf-8', errors='replace')"
                    log_error(f" Key decoded using fallback method: {decoding_method}")
                except Exception as e:
                    log_error(f"All key decoding methods failed: {e}")
                    raise GeneralErrorExcpetion(f"Failed to decode key file content: {e}")
        
        # Validate key content
        if not key_content:
            raise GeneralErrorExcpetion("Key content is empty after decoding")
        
        # Log key content details for debugging
        # log_info(f" Key content length: {len(key_content)} characters")
        # log_info(f" Key content preview: {key_content[:50]}...")
        # log_info(f" Key content ends with: ...{key_content[-20:]}")
        # log_info(f" Decoding method used: {decoding_method}")
        
        # Additional validation: check if key content looks like base64 or JSON
        # if key_content.startswith('{') and key_content.endswith('}'):
            # log_info(" Key content appears to be JSON format")
        # elif key_content.replace('+', '').replace('/', '').replace('=', '').isalnum():
            # log_info(" Key content appears to be base64 format")
        # else:
            # log_error("Key content format is unclear")
        
        # Decrypt the file
        plain_path = decrypt_file_from_oss(response_enc.content, key_content)
        # log_info(f"Decryption successful, temp file: {plain_path}")
        
        # Step 2: Upload to temp location
        with open(plain_path, 'rb') as f:
            decrypted_content = f.read()
        
        temp_object_name = f"temp/decrypted/{uuid.uuid4().hex}_{filename.replace('.enc', '')}"
        
        temp_upload = UploadFile(
            filename=temp_object_name.split('/')[-1],
            file=io.BytesIO(decrypted_content)
        )
        
        temp_upload_url = oss_client.generate_presigned_url(temp_object_name, expiration)
        oss_client.upload_file(temp_upload, temp_upload_url)
        
        # Step 3: Generate download URL
        temp_download_url = oss_client.download_file(temp_object_name, expiration)
        
        # Step 4: Register for 5-minute cleanup
        temp_id = await auto_cleanup_service.register_temp_file(temp_object_name, temp_download_url)
        
        # Clean up local file
        os.remove(plain_path)
        
        # log_info(f"File ready for download (5-min cleanup): {temp_object_name}")
        # log_info(f"Decryption completed successfully")
        return temp_download_url
        
    except Exception as e:
        log_error(f"Download with 5-min cleanup failed: {e}")
        raise

# Monitoring and management functions
async def get_cleanup_stats():
    """Get statistics about the cleanup service."""
    return auto_cleanup_service.get_stats()

async def run_manual_cleanup():
    """Run manual cleanup of expired files."""
    return await auto_cleanup_service.cleanup_expired_files()

async def force_cleanup_all():
    """Force cleanup of all temporary files."""
    return await auto_cleanup_service.force_cleanup_all() 