#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NW.js Automator Update System
Automatic update functionality for the NW.js Automator tool
"""

import os
import sys
import json
import hashlib
import requests
import shutil
import tempfile
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class UpdateSystem:
    """Handles automatic updates for NW.js Automator"""
    
    def __init__(self, current_version: str = "2.1.0"):
        self.current_version = current_version
        self.update_server = "https://api.github.com/repos/aeagisdev/rpgm-nwjs-automator"
        self.release_api = f"{self.update_server}/releases/latest"
        self.user_agent = f"NWJS-Automator/{current_version}"
        self.timeout = 30
        
    def check_for_updates(self) -> Optional[Dict]:
        """Check if a newer version is available"""
        try:
            logger.info("Checking for updates...")
            
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(
                self.release_api,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            # Compare versions
            if self._compare_versions(latest_version, self.current_version.lstrip('v')) > 0:
                logger.info(f"New version available: {latest_version}")
                return {
                    'version': latest_version,
                    'release_data': release_data,
                    'download_url': self._get_download_url(release_data)
                }
            else:
                logger.info("You're using the latest version")
                return None
                
        except requests.RequestException as e:
            logger.warning(f"Update check failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during update check: {e}")
            return None
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
        def parse_version(v: str) -> Tuple[int, ...]:
            return tuple(map(int, (v.split(".") + [0, 0, 0])[:3]))
        
        v1_parts = parse_version(v1)
        v2_parts = parse_version(v2)
        
        if v1_parts > v2_parts:
            return 1
        elif v1_parts < v2_parts:
            return -1
        else:
            return 0
    
    def _get_download_url(self, release_data: Dict) -> Optional[str]:
        """Get the appropriate download URL for the current platform"""
        current_platform = platform.system().lower()
        
        for asset in release_data.get('assets', []):
            asset_name = asset.get('name', '').lower()
            
            if current_platform == 'windows':
                if 'win' in asset_name and 'zip' in asset_name:
                    return asset['browser_download_url']
            elif current_platform == 'darwin':
                if 'mac' in asset_name and 'zip' in asset_name:
                    return asset['browser_download_url']
            elif current_platform == 'linux':
                if 'linux' in asset_name and ('tar' in asset_name or 'zip' in asset_name):
                    return asset['browser_download_url']
        
        # Fallback to source code if no platform-specific build found
        for asset in release_data.get('assets', []):
            if 'source' in asset.get('name', '').lower():
                return asset['browser_download_url']
        
        return None
    
    def download_update(self, download_url: str, target_dir: Path) -> Optional[Path]:
        """Download the update package"""
        try:
            logger.info(f"Downloading update from: {download_url}")
            
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix='nwjs_automator_update_'))
            temp_file = temp_dir / "update_package"
            
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            logger.info(f"Download progress: {percent:.1f}%")
            
            logger.info(f"✓ Update downloaded to: {temp_file}")
            return temp_file
            
        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            return None
    
    def verify_download(self, file_path: Path, expected_checksum: Optional[str] = None) -> bool:
        """Verify the integrity of the downloaded file"""
        try:
            if not file_path.exists():
                logger.error("Download file not found")
                return False
            
            # Calculate SHA-256 checksum
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_checksum = sha256_hash.hexdigest()
            logger.info(f"File checksum: {actual_checksum}")
            
            if expected_checksum and actual_checksum != expected_checksum:
                logger.error("Checksum verification failed")
                return False
            
            logger.info("✓ Download verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    def install_update(self, update_file: Path, install_dir: Path) -> bool:
        """Install the update"""
        try:
            logger.info(f"Installing update from: {update_file}")
            
            # Create backup of current installation
            backup_dir = install_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if install_dir.exists():
                logger.info(f"Creating backup at: {backup_dir}")
                shutil.copytree(install_dir, backup_dir)
            
            # Extract the update
            if update_file.suffix == '.zip':
                import zipfile
                with zipfile.ZipFile(update_file, 'r') as zip_ref:
                    zip_ref.extractall(install_dir)
            elif update_file.suffix in ('.tar', '.gz', '.tar.gz'):
                import tarfile
                with tarfile.open(update_file, 'r:gz') as tar_ref:
                    tar_ref.extractall(install_dir)
            else:
                # For source code or other formats, just copy
                shutil.copy2(update_file, install_dir / update_file.name)
            
            logger.info("✓ Update installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return False
    
    def get_changelog(self, release_data: Dict) -> str:
        """Get the changelog for the latest version"""
        return release_data.get('body', 'No changelog available')
    
    def get_release_notes(self, release_data: Dict) -> str:
        """Get formatted release notes"""
        version = release_data.get('tag_name', 'Unknown')
        published_at = release_data.get('published_at', 'Unknown date')
        changelog = self.get_changelog(release_data)
        
        return f"""
🚀 New Version Available: {version}
📅 Released: {published_at}

📋 Changelog:
{changelog}
"""


def check_updates_interactive():
    """Interactive update check"""
    update_system = UpdateSystem()
    
    print("🔄 NW.js Automator Update System")
    print("=" * 50)
    
    update_info = update_system.check_for_updates()
    
    if update_info:
        print(update_system.get_release_notes(update_info['release_data']))
        
        choice = input("\n💡 Do you want to download and install this update? (Y/n): ").strip().lower()
        
        if choice != 'n':
            print("\n📥 Starting download...")
            download_path = update_system.download_update(
                update_info['download_url'],
                Path.cwd()
            )
            
            if download_path:
                if update_system.verify_download(download_path):
                    install_choice = input("\n🔧 Install the update now? (Y/n): ").strip().lower()
                    if install_choice != 'n':
                        if update_system.install_update(download_path, Path.cwd()):
                            print("\n✅ Update installed successfully!")
                            print("💾 Please restart the application to use the new version.")
                        else:
                            print("\n❌ Update installation failed.")
                    else:
                        print("\n⏸️  Update installation cancelled.")
                else:
                    print("\n❌ Download verification failed. Update aborted.")
            else:
                print("\n❌ Download failed.")
        else:
            print("\n⏸️  Update cancelled.")
    else:
        print("\n✅ You're using the latest version!")


if __name__ == "__main__":
    check_updates_interactive()