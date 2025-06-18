#!/usr/bin/env python3
"""
RPG Maker MV NW.js Automation Script
Automates the process of updating RPG Maker MV's NW.js runtime

Copyright (c) 2025 Andrea Giuseppe Santagati
Licensed under the MIT License - see LICENSE file for details
https://github.com/aeagisdev/rpgm-nwjs-automator
"""

import os
import sys
import json
import shutil
import zipfile
import requests
import tarfile
import subprocess
import platform
from pathlib import Path
from urllib.parse import urlparse
import argparse
import logging

# Windows-specific imports for creating shortcuts
if sys.platform == 'win32':
    try:
        import win32com.client
        import pythoncom
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
        logging.warning("win32com not available. Shortcut creation will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class NWJSAutomator:
    def __init__(self, game_path, nwjs_path=None, nwjs_version="v0.49.2", use_sdk=True, executable_name="Game"):
        self.game_path = Path(game_path)
        self.nwjs_path = Path(nwjs_path) if nwjs_path else None
        self.nwjs_version = nwjs_version
        self.use_sdk = use_sdk
        self.executable_name = executable_name
        self.nwjs_url_base = "https://dl.nwjs.io"
        
        # Files/folders to keep from original game - UPDATED to include index.html
        self.keep_files = ['package.json', 'www', 'index.html']
        
        # Files to remove after copying NW.js
        self.cleanup_files = [
        # Development and debugging tools
        'chromedriver',
        'chromedriver.exe',
        'nw_100_percent.pak',
        'nw_200_percent.pak',
        
        # Documentation and credits
        'ACKNOWLEDGEMENTS',
        'AUTHORS',
        'CHANGELOG.md',
        'LICENSE',
        'README.md',
        'credits.html',
        
        # Development versions and SDK-specific files (if not needed)
        'payload',
        'debug.log',
        'pnacl',
        
        # Locale files (keep only essential ones)
        # Note: We'll handle locales directory separately to keep only en-US
        
        # Other optional files
        'notification_helper.exe',  # Windows notification helper
        'chrome_100_percent.pak',
        'chrome_200_percent.pak'
    ]
    
    def validate_game_directory(self):
        """Validate that the provided path is a valid RPG Maker MV game directory"""
        if not self.game_path.exists():
            raise FileNotFoundError(
                f"Game directory not found: {self.game_path}")

        package_json = self.game_path / 'package.json'
        www_folder = self.game_path / 'www'

        if not package_json.exists():
            raise FileNotFoundError(
                "package.json not found. This may not be an RPG Maker MV game.")

        if not www_folder.exists():
            raise FileNotFoundError(
                "www folder not found. This may not be an RPG Maker MV game.")

        # Validate and fix package.json
        try:
            self.validate_and_fix_package_json(package_json)
        except Exception as e:
            logger.error(f"Failed to validate/fix package.json: {e}")
            raise
        logger.info(f"✓ Valid RPG Maker MV game found at: {self.game_path}")

    def validate_and_fix_package_json(self, package_json_path):
        """Validate and fix package.json for NW.js compatibility"""
        logger.info("Validating package.json...")

        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in package.json: {e}")
        except Exception as e:
            raise ValueError(f"Could not read package.json: {e}")

        # Check and fix required fields for NW.js
        fixes_made = False

        # 1. Check 'name' field (required by NW.js)
        if 'name' not in package_data or not package_data['name']:
            game_name = self.game_path.name.replace(' ', '-').lower()
            package_data['name'] = game_name
            logger.info(f"  Fixed: Added missing 'name' field: {game_name}")
            fixes_made = True

        # Save the fixed package.json if any fixes were made
        if fixes_made:
            try:
                with open(package_json_path, 'w', encoding='utf-8') as f:
                    json.dump(package_data, f, indent=2, ensure_ascii=False)
                logger.info("✓ package.json fixes saved")
            except Exception as e:
                logger.error(f"Could not save package.json fixes: {e}")
                raise
    
    def get_nwjs_download_url(self):
        """Get the download URL for the specified NW.js version"""
        arch_map = {
            'AMD64': 'x64',
            'x86_64': 'x64',
            'arm64': 'arm64',
            'i386': 'ia32',
            'x86': 'ia32'
        }
        
        arch = arch_map.get(platform.machine(), 'x64')
        
        # Map platform names
        platform_map = {
            'win32': 'win',
            'darwin': 'osx',
            'linux': 'linux'
        }
        
        platform_name = platform_map.get(sys.platform, 'win')
        
        # Use the version specified, defaulting to v0.49.2
        version = self.nwjs_version if self.nwjs_version.startswith('v') else f"v{self.nwjs_version}"
        
        if self.use_sdk:
            filename = f"nwjs-sdk-{version}-{platform_name}-{arch}"
        else:
            filename = f"nwjs-{version}-{platform_name}-{arch}"
        
        if platform_name == 'win':
            filename += '.zip'
        else:
            filename += '.tar.gz'
        
        return f"{self.nwjs_url_base}/{version}/{filename}", filename

    def download_nwjs(self, output_dir):
        """Download NW.js if not already provided"""
        url, filename = self.get_nwjs_download_url()
        output_path = Path(output_dir) / filename
        
        logger.info(f"Downloading NW.js from: {url}")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"✓ Downloaded: {output_path}")
            return output_path
            
        except requests.RequestException as e:
            logger.error(f"Failed to download NW.js: {e}")
            raise

    def extract_nwjs(self, archive_path, extract_dir):
        """Extract NW.js archive"""
        logger.info(f"Extracting NW.js archive: {archive_path}")
        
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif archive_path.suffix == '.gz':
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
        
        # Find the extracted NW.js directory
        for item in Path(extract_dir).iterdir():
            if item.is_dir() and 'nwjs' in item.name.lower():
                logger.info(f"✓ NW.js extracted to: {item}")
                return item
        
        raise FileNotFoundError("Could not find extracted NW.js directory")

    def backup_game(self):
        """Create a backup of the original game"""
        backup_path = self.game_path.parent / f"{self.game_path.name}_backup"
        
        if backup_path.exists():
            logger.info(f"Backup already exists: {backup_path}")
            return backup_path
        
        logger.info(f"Creating backup: {backup_path}")
        shutil.copytree(self.game_path, backup_path)
        logger.info("✓ Backup created successfully")
        return backup_path

    def save_important_files(self):
        """Save package.json, www folder, and index.html before cleaning"""
        logger.info("Saving important files (package.json, www folder, and index.html)...")

        temp_dir = self.game_path.parent / f"temp_{self.game_path.name}_files"
        temp_dir.mkdir(exist_ok=True)
        critical_files = ['package.json', 'www']
        missing_files = []

        # Save package.json
        package_json = self.game_path / 'package.json'
        if package_json.exists():
            shutil.copy2(package_json, temp_dir / 'package.json')
            logger.info("  Saved: package.json")

        # Save www folder
        www_folder = self.game_path / 'www'
        if www_folder.exists():
            shutil.copytree(www_folder, temp_dir / 'www', dirs_exist_ok=True)
            logger.info("  Saved: www folder")

        # Save index.html (CRITICAL for NW.js to work) - FIXED PATH
        index_html = self.game_path / 'index.html'
        if index_html.exists():
            shutil.copy2(index_html, temp_dir / 'index.html')  # Changed from 'www/index.html' to 'index.html'
            logger.info("  Saved: index.html")
        else:
            logger.warning("  index.html not found - this may cause issues!")

        
        for file in critical_files:
            if not (temp_dir / file).exists():
                missing_files.append(file)
            
        if missing_files:
            logger.error(f"Critical files not saved to temp directory: {missing_files}")
            logger.error("Aborting to prevent data loss!")
            raise FileNotFoundError(f"Failed to backup critical files: {missing_files}")

        logger.info(f"✓ Important files saved to: {temp_dir}")
        return temp_dir

    def clean_game_directory(self):
        """Delete everything inside game folder except what we saved"""
        logger.info("Cleaning game directory (deleting everything)...")
        
        removed_count = 0
        
        for item in self.game_path.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                removed_count += 1
                logger.info(f"  Removed: {item.name}")
            except Exception as e:
                logger.warning(f"  Could not remove {item.name}: {e}")
        
        logger.info(f"✓ Removed {removed_count} items from game directory")

    def restore_important_files(self, temp_dir):
        """Restore package.json, www folder, and index.html after copying NW.js"""
        logger.info("Restoring important files...")

        # Restore package.json
        temp_package_json = temp_dir / 'package.json'
        if temp_package_json.exists():
            dest_package_json = self.game_path / 'package.json'
            if dest_package_json.exists():
                dest_package_json.unlink()
            shutil.copy2(temp_package_json, dest_package_json)
            logger.info("  Restored: package.json")

        # Restore www folder
        temp_www = temp_dir / 'www'
        if temp_www.exists():
            dest_www = self.game_path / 'www'
            if dest_www.exists():
                shutil.rmtree(dest_www)
            shutil.copytree(temp_www, dest_www)
            logger.info("  Restored: www folder")

        # Restore index.html (CRITICAL for NW.js to work)
        temp_index_html = temp_dir / 'index.html'
        if temp_index_html.exists():
            dest_index_html = self.game_path / 'index.html'
            if dest_index_html.exists():
                dest_index_html.unlink()
            shutil.copy2(temp_index_html, dest_index_html)
            logger.info("  Restored: index.html")
        else:
            # Check if index.html exists in www folder and copy it to root
            www_index_html = self.game_path / 'www' / 'index.html'
            if www_index_html.exists():
                shutil.copy2(www_index_html, self.game_path / 'index.html')
                logger.info("  Copied index.html from www folder to root")
            else:
                # If index.html is missing, create a basic one
                logger.warning(
                    "  index.html not found in backup, creating a basic one...")
                self.create_basic_index_html()

        # Re-validate package.json after restoration
        package_json_path = self.game_path / 'package.json'
        if package_json_path.exists():
            self.validate_and_fix_package_json(package_json_path)

        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir)
            logger.info("✓ Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Could not clean up temp directory: {e}")
    
    def create_basic_index_html(self):
        """Create a basic index.html file if missing"""
        index_html_path = self.game_path / "index.html"

        # Scan www/js directory for existing files
        js_dir = self.game_path / "www" / "js"
        script_tags = []

        if js_dir.exists():
            # Define expected file order for RPG Maker MV
            libs_order = [
                "pixi.js",
                "pixi-tilemap.js",
                "pixi-picture.js",
                "fpsmeter.js",
                "lz-string.js",
            ]
            core_order = [
                "rpg_core.js",
                "rpg_managers.js",
                "rpg_objects.js",
                "rpg_scenes.js",
                "rpg_sprites.js",
                "rpg_windows.js",
            ]

            # Check libs directory
            libs_dir = js_dir / "libs"
            if libs_dir.exists():
                for lib_file in libs_order:
                    lib_path = libs_dir / lib_file
                    if lib_path.exists():
                        script_tags.append(
                            f'    <script type="text/javascript" src="js/libs/{lib_file}"></script>'
                        )

            # Check core files
            for core_file in core_order:
                core_path = js_dir / core_file
                if core_path.exists():
                    script_tags.append(
                        f'    <script type="text/javascript" src="js/{core_file}"></script>'
                    )

            # Always add plugins.js and main.js if they exist
            for final_file in ["plugins.js", "main.js"]:
                final_path = js_dir / final_file
                if final_path.exists():
                    script_tags.append(
                        f'    <script type="text/javascript" src="js/{final_file}"></script>'
                    )

        # If no scripts found, add minimal main.js
        if not script_tags:
            script_tags.append(
                '    <script type="text/javascript" src="js/main.js"></script>'
            )
        basic_html = f'''<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="apple-mobile-web-app-capable" content="yes">
                <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
                <meta name="viewport" content="user-scalable=no">
                <link rel="icon" href="icon/icon.png" type="image/png">
                <title>RPG Game</title>
                <style type="text/css">
                    body {{
                        margin: 0;
                        padding: 0;
                    }}
                    canvas {{
                        cursor: default;
                    }}
                </style>
            </head>
            <body style="background-color: black">
            {chr(10).join(script_tags)}
            </body>
            </html>'''
            
            try:
                with open(index_html_path, 'w', encoding='utf-8') as f:
                    f.write(basic_html)
                logger.info("  Created: basic index.html with detected JS files")
            except Exception as e:
                logger.error(f"Could not create basic index.html: {e}")
                raise

    
    def copy_nwjs_to_game(self, nwjs_dir):
        """Copy NW.js runtime files to the game directory"""
        logger.info(f"Copying NW.js runtime files from {nwjs_dir} to {self.game_path}...")
        copied_count = 0

        # Copy all NW.js files to the game directory
        for item in nwjs_dir.iterdir():
            dest_path = self.game_path / item.name

            try:
                if item.is_dir():
                    shutil.copytree(item, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest_path)
                    
                    # Fix permissions for executable files on Unix systems
                    if sys.platform != 'win32' and item.name in ['nw', 'nwjs']:
                        dest_path.chmod(0o755)

                copied_count += 1
                logger.info(f"  Copied: {item.name}")

        logger.info(f"✓ Copied {copied_count} NW.js runtime files to game directory")

    def rename_executable(self):
        """Rename nw.exe to custom executable name"""
        logger.info(f"Renaming NW.js executable to {self.executable_name}...")

        # Platform-specific executable names with fallback detection
        possible_executables = []

        if sys.platform == 'win32':
            possible_executables = ['nw.exe', 'nwjs.exe']
            game_exe_name = f'{self.executable_name}.exe'
        elif sys.platform == 'darwin':  # macOS
            possible_executables = ['nwjs', 'nw']
            game_exe_name = self.executable_name
        else:  # Linux
            possible_executables = ['nw', 'nwjs']
            game_exe_name = self.executable_name

        # Find the actual NW.js executable
        nw_exe = None
        for exe_name in possible_executables:
            potential_exe = self.game_path / exe_name
            if potential_exe.exists():
                nw_exe = potential_exe
                break
            
        if not nw_exe:
            logger.error(f"NW.js executable not found. Looked for: {possible_executables}")
            return None

        game_exe = self.game_path / game_exe_name

        try:
            if game_exe.exists():
                game_exe.unlink()

            nw_exe.rename(game_exe)

            # Make executable on Unix-like systems
            if sys.platform != 'win32':
                game_exe.chmod(0o755)

            logger.info(f"✓ Renamed {nw_exe.name} to {game_exe.name}")
            return game_exe

        except Exception as e:
            logger.error(f"Could not rename executable: {e}")
            return nw_exe

    def cleanup_nwjs_files(self):
        logger.info("Cleaning up unnecessary NW.js files...")

        removed_count = 0

        for file_name in self.cleanup_files:
            file_path = self.game_path / file_name
            if file_path.exists():
                try:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    removed_count += 1
                    logger.info(f"  Removed: {file_name}")
                except Exception as e:
                    logger.warning(f"  Could not remove {file_name}: {e}")

        # Handle locale directory cleanup - keep only en-US
        locales_dir = self.game_path / 'locales'
        if locales_dir.exists() and locales_dir.is_dir():
            try:
                for locale_file in locales_dir.iterdir():
                    if locale_file.name not in ['en-US.pak', 'en-US.pak.info']:
                        if locale_file.is_file():
                            locale_file.unlink()
                            removed_count += 1
                            logger.info(f"  Removed: locales/{locale_file.name}")
            except Exception as e:
                logger.warning(f"  Could not clean locales directory: {e}")

        if removed_count > 0:
            logger.info(f"✓ Removed {removed_count} unnecessary files")
        else:
            logger.info("✓ No unnecessary files to remove")

    def setup_nwjs(self):
        """Setup NW.js - download if needed"""
        if self.nwjs_path and self.nwjs_path.exists():
            logger.info(f"Using existing NW.js: {self.nwjs_path}")
            return self.nwjs_path
        # Download and extract NW.js
        temp_dir = Path.cwd() / 'temp_nwjs'
        temp_dir.mkdir(exist_ok=True)
        try:
            archive_path = self.download_nwjs(temp_dir)
            nwjs_dir = self.extract_nwjs(archive_path, temp_dir)
            logger.info(f"✓ NW.js setup complete: {nwjs_dir}")
            return nwjs_dir
        except Exception as e:
            logger.error(f"Failed to setup NW.js: {e}")
            raise



    def cleanup_temp_files(self):
        """Clean up temporary files"""
        temp_dir = Path.cwd() / 'temp_nwjs'
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                logger.info("✓ Cleaned up temporary NW.js files")
            except Exception as e:
                logger.warning(f"Could not clean up temporary files: {e}")

    def create_shortcut_windows(self, game_exe):
        """Create a Windows shortcut (optional enhancement)"""
        if not WIN32_AVAILABLE:
            return None
        
        game_name = self.executable_name
        shortcut_path = self.game_path / f"{game_name}.lnk"
        
        try:
            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(str(shortcut_path))
            shortcut.TargetPath = str(game_exe)
            shortcut.WorkingDirectory = str(self.game_path)
            shortcut.Description = f"Launch {game_name}"
            shortcut.Save()
            logger.info(f"✓ Created Windows shortcut: {shortcut_path}")
            return shortcut_path
            
        except Exception as e:
            logger.warning(f"Could not create Windows shortcut: {e}")
            return None
        finally:
            pythoncom.CoUninitialize()

    def process_game(self, create_backup=True):
        logger.info(f"Starting NW.js update for: {self.game_path}")
        
        try:
            # Step 0: Validate game directory
            self.validate_game_directory()
            
            # Step 0.5: Create backup if requested
            if create_backup:
                self.backup_game()
            
            # Step 1: Setup NW.js (download SDK build)
            nwjs_dir = self.setup_nwjs()
            
            # Step 3a: Save package.json, www folder, and index.html
            temp_dir = self.save_important_files()
                        
            # Step 3b: Delete everything inside game folder
            self.clean_game_directory()
            
            # Step 3b: Copy NW.js files to game directory
            self.copy_nwjs_to_game(nwjs_dir)
            
            # Step 3c: Restore package.json, www folder, and index.html
            self.restore_important_files(temp_dir)
            
            # Step 3c: Rename nw.exe to custom executable name
            game_exe = self.rename_executable()
            
            # Step 3d: Delete chromedriver (and other cleanup)
            self.cleanup_nwjs_files()
            
            if not game_exe:
                raise FileNotFoundError("Could not create game executable")
            
            # Optional: Create shortcut on Windows
            if sys.platform == 'win32':
                self.create_shortcut_windows(game_exe)
            
            # Cleanup temporary files
            self.cleanup_temp_files()
            
            logger.info("🎉 NW.js update completed successfully!")
            logger.info(f"🚀 Launch the game using: {game_exe}")
            logger.info("💡 Type 'process.versions' in the game console to check your new NW.js version!")
            
            return {
                'success': True,
                'game_executable': game_exe,
                'game_path': self.game_path
            }
            
        except Exception as e:
            logger.error(f"❌ Update failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def get_user_input():
    """Get user input for configuration options"""
    print("🎮 RPG Maker MV NW.js Update Automation Tool")
    print("=" * 80)
    
    # Get game path
    while True:
        game_path = input("\n📁 Enter the path to your RPG Maker MV game directory: ").strip()
        if game_path:
            game_path = game_path.strip('"\'')  # Remove quotes if present
            if Path(game_path).exists():
                break
            else:
                print("❌ Directory not found. Please enter a valid path.")
        else:
            print("❌ Please enter a valid path.")
    
    # Get custom executable name
    print("\n🎯 Executable Name:")
    executable_name = input("Enter the name for your game executable (default: Game): ").strip()
    if not executable_name:
        executable_name = "Game"
    # Remove .exe extension if provided (will be added automatically on Windows)
    if executable_name.lower().endswith('.exe'):
        executable_name = executable_name[:-4]
    
    # Get NW.js path (optional)
    nwjs_path = input("\n⚙️  Enter path to existing NW.js installation (press Enter to download): ").strip()
    nwjs_path = nwjs_path.strip('"\'') if nwjs_path else None
    
    # Get NW.js version
    print("\n🔧 NW.js Version Options:")
    print("  1. v0.29.4 (Maximum compatibility - original RPG Maker MV era)")
    print("  2. v0.49.2 (Balanced - good performance with broad compatibility)")  
    print("  3. v0.72.0 (Modern stable - last version supporting Windows 7)")
    print("  4. v0.90.0+ (Latest stable - best performance, requires Windows 10+)")
    print("  5. Custom version")

    while True:
        version_choice = input("\nSelect version (1-5) or press Enter for balanced default: ").strip()
        if not version_choice or version_choice == "2":
            nwjs_version = "v0.49.2"  # Keep as balanced default
            break
        elif version_choice == "1":
            nwjs_version = "v0.29.4"
            break
        elif version_choice == "3":
            nwjs_version = "v0.72.0"
            break
        elif version_choice == "4":
            nwjs_version = "v0.90.0"
            break
        elif version_choice == "5":
            custom_version = input("Enter custom version (e.g., v0.100.1): ").strip()
            if custom_version:
                nwjs_version = custom_version if custom_version.startswith('v') else f'v{custom_version}'
                break
        print("❌ Invalid choice. Please select 1, 2, 3, 4, 5, or press Enter.")
    
    # Get build type
    use_sdk = input("\n🛠️  Use SDK build? (Y/n): ").strip().lower()
    use_sdk = use_sdk != 'n'
    
    # Get backup preference
    create_backup = input("\n💾 Create backup before processing? (Y/n): ").strip().lower()
    create_backup = create_backup != 'n'
    
    # Verbose logging
    verbose = input("\n📝 Enable verbose logging? (y/N): ").strip().lower()
    verbose = verbose == 'y'
    
    return {
        'game_path': game_path,
        'executable_name': executable_name,
        'nwjs_path': nwjs_path,
        'nwjs_version': nwjs_version,
        'use_sdk': use_sdk,
        'create_backup': create_backup,
        'verbose': verbose
    }

def main():
    parser = argparse.ArgumentParser(description='Automate NW.js update for RPG Maker MV games')
    parser.add_argument('--game-path', help='Path to the RPG Maker MV game directory')
    parser.add_argument('--executable-name', default='Game', help='Name for the game executable (default: Game)')
    parser.add_argument('--nwjs-path', help='Path to existing NW.js installation (optional)')
    parser.add_argument('--nwjs-version', default='v0.49.2', help='NW.js version to download (default: v0.49.2)')
    parser.add_argument('--no-sdk', action='store_true', help='Use normal build instead of SDK build')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # If no game path provided or interactive mode requested, use interactive input
    if not args.game_path or args.interactive:
        config = get_user_input()
        
        if config['verbose']:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Create automator instance
        automator = NWJSAutomator(
            game_path=config['game_path'],
            nwjs_path=config['nwjs_path'],
            nwjs_version=config['nwjs_version'],
            use_sdk=config['use_sdk'],
            executable_name=config['executable_name']
        )
        
        # Show configuration summary
        print(f"\n📋 Configuration Summary:")
        print(f"   Game Path: {config['game_path']}")
        print(f"   Executable Name: {config['executable_name']}")
        print(f"   NW.js Version: {config['nwjs_version']}")
        print(f"   Build Type: {'SDK' if config['use_sdk'] else 'Normal'}")
        print(f"   Create Backup: {'Yes' if config['create_backup'] else 'No'}")
        if config['nwjs_path']:
            print(f"   NW.js Path: {config['nwjs_path']}")
        
        confirm = input(f"\n🚀 Proceed with automation? (Y/n): ").strip().lower()
        if confirm == 'n':
            print("❌ Operation cancelled by user.")
            sys.exit(0)
        
        # Process the game
        result = automator.process_game(create_backup=config['create_backup'])
    else:
        # Use command line arguments
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Clean executable name (remove .exe if provided)
        executable_name = args.executable_name
        if executable_name.lower().endswith('.exe'):
            executable_name = executable_name[:-4]
        
        # Create automator instance
        automator = NWJSAutomator(
            game_path=args.game_path,
            nwjs_path=args.nwjs_path,
            nwjs_version=args.nwjs_version,
            use_sdk=not args.no_sdk,
            executable_name=executable_name
        )
        
        # Process the game
        result = automator.process_game(create_backup=not args.no_backup)
    
    if result['success']:
        print(f"\n✅ Success! Game processed successfully.")
        print(f"📁 Game directory: {result['game_path']}")
        print(f"🚀 Game executable: {result['game_executable']}")
        print(f"\n🎮 You can now launch your game using your custom executable!")
        print(f"💡 Type 'process.versions' in the game console to verify your NW.js version!")
        
    else:
        print(f"\n❌ Failed: {result['error']}")
        sys.exit(1)

if __name__ == '__main__':
    main()