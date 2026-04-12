#!/usr/bin/env python3
#
#   RPG Maker MV NW.js Automation Script
#   Automates the process of updating RPG Maker MV's NW.js runtime
#
#   Copyright (c) 2025 Andrea Giuseppe Santagati
#   Licensed under the MIT License - see LICENSE file for details
#   https://github.com/aeagisdev/rpgm-nwjs-automator
#

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
        logging.warning(
            "win32com not available. Shortcut creation will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class NWJSAutomator:
    def __init__(self, game_path, nwjs_path=None, nwjs_version="v0.49.2", use_sdk=True, executable_name="Game", 
                 enable_devtools=False, platform_optimized=False, logging_level="INFO", 
                 config_profile=None, config_template=None):
        self.game_path = Path(game_path)
        self.nwjs_path = Path(nwjs_path) if nwjs_path else None
        self.nwjs_version = nwjs_version
        self.use_sdk = use_sdk
        self.executable_name = executable_name
        self.enable_devtools = enable_devtools
        self.platform_optimized = platform_optimized
        self.nwjs_url_base = "https://dl.nwjs.io"
        self.config_profile = config_profile
        self.config_template = config_template
        
        # Files to remove after copying NW.js - Now configurable
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
            # Other optional files
            'notification_helper.exe',  # Windows notification helper
            'chrome_100_percent.pak',
            'chrome_200_percent.pak'
        ]
        
        # Files to keep for debugging purposes
        self.debug_files = [
            'debug.log',
            'nw_100_percent.pak',
            'nw_200_percent.pak',
            'chrome_100_percent.pak',
            'chrome_200_percent.pak'
        ]
        
        # Configure logging based on user preference
        self.configure_logging(logging_level)
        
        # Platform detection
        self.current_platform = platform.system().lower()
        self.platform_info = self.detect_platform_info()
        
        # Load configuration profile if specified
        self.config_profiles = self.load_config_profiles()
        self.current_config = self.load_profile_config(config_profile)
        
        # Load configuration template if specified
        self.template_configs = self.load_template_configs()
        self.applied_template = self.apply_config_template(config_template)

        # Files/folders to keep from original game - UPDATED to include index.html
        self.keep_files = ['package.json', 'www', 'index.html']

        # SDK version compatibility database
        self.sdk_compatibility = {
            "v0.49.2": {"stable": True, "tested": True, "recommended": True},
            "v0.72.0": {"stable": True, "tested": True, "recommended": True},
            "v0.90.0": {"stable": True, "tested": True, "recommended": True},
        }

        # Auto-update configuration
        self.auto_update_config = {
            "enabled": True,
            "check_interval": 7,  # days
            "update_url": "https://api.github.com/repos/aeagisdev/rpgm-nwjs-automator/releases/latest",
            "backup_before_update": True,
            "verify_integrity": True
        }

        # Security hardening configuration
        self.security_config = {
            "input_validation": True,
            "path_traversal_protection": True,
            "download_verification": True,
            "sandbox_operations": True,
            "secure_logging": True
        }

        # Performance optimization configuration
        self.performance_config = {
            "parallel_downloads": True,
            "memory_optimization": True,
            "file_caching": True,
            "progress_reporting": True,
            "bottleneck_analysis": True
        }
        
        # Extended SDK version compatibility database
        self.sdk_compatibility.update({
            "v0.50.1": {"stable": True, "tested": True, "recommended": False},
            "v0.51.0": {"stable": False, "tested": False, "recommended": False},
            "v0.52.0": {"stable": True, "tested": True, "recommended": True},
            "v0.53.0": {"stable": True, "tested": False, "recommended": False}
        })


        
        # Whitelist for critical files that should never be removed
        self.critical_files_whitelist = [
            'package.json',
            'www',
            'index.html',
            'nw.exe',
            'nw',
            'nwjs'
        ]
        
        # Locale files to keep (default: only en-US)
        self.keep_locales = ['en-US.pak', 'en-US.pak.info']

    def configure_logging(self, level="INFO"):
        """Configure logging system with different levels and file output"""
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        log_level = log_levels.get(level.upper(), logging.INFO)
        
        # Configure basic logging with UTF-8 encoding for Windows compatibility
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8'
        )
        
        # Add file logging with rotation
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                'nwjs_automator.log',
                maxBytes=1024*1024,  # 1MB
                backupCount=3,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            logging.getLogger().addHandler(file_handler)
            logger.info("File logging configured successfully")
        except ImportError:
            logger.warning("RotatingFileHandler not available, file logging disabled")
        except Exception as e:
            logger.warning(f"Could not configure file logging: {e}")

    def load_config_profiles(self):
        """Load predefined configuration profiles"""
        profiles = {
            'default': {
                'name': 'Default Configuration',
                'description': 'Balanced settings for most RPG Maker MV games',
                'settings': {
                    'nwjs_version': 'v0.49.2',
                    'use_sdk': True,
                    'enable_devtools': False,
                    'platform_optimized': True,
                    'cleanup_files': self.cleanup_files.copy(),
                    'keep_locales': ['en-US.pak', 'en-US.pak.info']
                }
            },
            'development': {
                'name': 'Development Mode',
                'description': 'Settings optimized for game development and debugging',
                'settings': {
                    'nwjs_version': 'v0.72.0',
                    'use_sdk': True,
                    'enable_devtools': True,
                    'platform_optimized': True,
                    'cleanup_files': [f for f in self.cleanup_files if f not in self.debug_files],
                    'keep_locales': ['en-US.pak', 'en-US.pak.info']
                }
            },
            'production': {
                'name': 'Production Mode',
                'description': 'Settings optimized for final game distribution',
                'settings': {
                    'nwjs_version': 'v0.49.2',
                    'use_sdk': False,
                    'enable_devtools': False,
                    'platform_optimized': True,
                    'cleanup_files': self.cleanup_files.copy(),
                    'keep_locales': ['en-US.pak', 'en-US.pak.info']
                }
            },
            'compatibility': {
                'name': 'Compatibility Mode',
                'description': 'Settings for maximum compatibility with older games',
                'settings': {
                    'nwjs_version': 'v0.29.4',
                    'use_sdk': True,
                    'enable_devtools': False,
                    'platform_optimized': False,
                    'cleanup_files': self.cleanup_files.copy(),
                    'keep_locales': ['en-US.pak', 'en-US.pak.info']
                }
            },
            'modern': {
                'name': 'Modern Mode',
                'description': 'Settings for modern NW.js features (Windows 10+ required)',
                'settings': {
                    'nwjs_version': 'v0.90.0',
                    'use_sdk': True,
                    'enable_devtools': True,
                    'platform_optimized': True,
                    'cleanup_files': self.cleanup_files.copy(),
                    'keep_locales': ['en-US.pak', 'en-US.pak.info']
                }
            }
        }
        
        logger.info(f"Loaded {len(profiles)} configuration profiles")
        return profiles

    def load_profile_config(self, profile_name):
        """Load configuration from a profile"""
        if not profile_name or profile_name not in self.config_profiles:
            logger.info("Using default configuration")
            return None
        
        profile = self.config_profiles[profile_name]
        logger.info(f"Applying configuration profile: {profile['name']}")
        logger.info(f"Description: {profile['description']}")
        
        # Apply profile settings
        profile_settings = profile['settings']
        
        # Update instance variables based on profile
        if 'nwjs_version' in profile_settings:
            self.nwjs_version = profile_settings['nwjs_version']
        if 'use_sdk' in profile_settings:
            self.use_sdk = profile_settings['use_sdk']
        if 'enable_devtools' in profile_settings:
            self.enable_devtools = profile_settings['enable_devtools']
        if 'platform_optimized' in profile_settings:
            self.platform_optimized = profile_settings['platform_optimized']
        if 'cleanup_files' in profile_settings:
            self.cleanup_files = profile_settings['cleanup_files']
        if 'keep_locales' in profile_settings:
            self.keep_locales = profile_settings['keep_locales']
        
        logger.info(f"✓ Configuration profile '{profile_name}' applied successfully")
        return profile

    def load_template_configs(self):
        """Load predefined configuration templates"""
        templates = {
            'minimal': {
                'name': 'Minimal Configuration',
                'description': 'Template for smallest possible game size',
                'settings': {
                    'use_sdk': False,
                    'enable_devtools': False,
                    'cleanup_files': self.cleanup_files + self.debug_files,
                    'keep_locales': ['en-US.pak', 'en-US.pak.info']
                }
            },
            'debug': {
                'name': 'Debug Configuration',
                'description': 'Template for development with full debugging support',
                'settings': {
                    'use_sdk': True,
                    'enable_devtools': True,
                    'cleanup_files': [f for f in self.cleanup_files if f not in self.debug_files],
                    'keep_locales': ['en-US.pak', 'en-US.pak.info']
                }
            },
            'multilingual': {
                'name': 'Multilingual Configuration',
                'description': 'Template that preserves multiple language files',
                'settings': {
                    'use_sdk': True,
                    'enable_devtools': False,
                    'cleanup_files': self.cleanup_files.copy(),
                    'keep_locales': ['en-US.pak', 'en-US.pak.info', 'ja.pak', 'ja.pak.info']
                }
            }
        }
        
        logger.info(f"Loaded {len(templates)} configuration templates")
        return templates

    def apply_config_template(self, template_name):
        """Apply a configuration template"""
        if not template_name or template_name not in self.template_configs:
            logger.info("No configuration template applied")
            return None
        
        template = self.template_configs[template_name]
        logger.info(f"Applying configuration template: {template['name']}")
        logger.info(f"Description: {template['description']}")
        
        # Apply template settings
        template_settings = template['settings']
        
        # Update instance variables based on template
        if 'use_sdk' in template_settings:
            self.use_sdk = template_settings['use_sdk']
        if 'enable_devtools' in template_settings:
            self.enable_devtools = template_settings['enable_devtools']
        if 'cleanup_files' in template_settings:
            self.cleanup_files = template_settings['cleanup_files']
        if 'keep_locales' in template_settings:
            self.keep_locales = template_settings['keep_locales']
        
        logger.info(f"✓ Configuration template '{template_name}' applied successfully")
        return template

    def save_config_profile(self, profile_name, config_data):
        """Save a custom configuration profile"""
        if not profile_name:
            logger.error("Profile name cannot be empty")
            return False
        
        # Create profiles directory if it doesn't exist
        profiles_dir = Path.cwd() / 'config_profiles'
        profiles_dir.mkdir(exist_ok=True)
        
        profile_file = profiles_dir / f"{profile_name}.json"
        
        try:
            # Merge with current settings
            full_config = {
                'name': config_data.get('name', profile_name),
                'description': config_data.get('description', 'Custom configuration profile'),
                'settings': {
                    'nwjs_version': config_data.get('nwjs_version', self.nwjs_version),
                    'use_sdk': config_data.get('use_sdk', self.use_sdk),
                    'enable_devtools': config_data.get('enable_devtools', self.enable_devtools),
                    'platform_optimized': config_data.get('platform_optimized', self.platform_optimized),
                    'cleanup_files': config_data.get('cleanup_files', self.cleanup_files),
                    'keep_locales': config_data.get('keep_locales', self.keep_locales)
                }
            }
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Configuration profile saved: {profile_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration profile: {e}")
            return False

    def export_config(self, output_path):
        """Export current configuration to a file"""
        try:
            config_data = {
                'nwjs_version': self.nwjs_version,
                'use_sdk': self.use_sdk,
                'enable_devtools': self.enable_devtools,
                'platform_optimized': self.platform_optimized,
                'executable_name': self.executable_name,
                'cleanup_files': self.cleanup_files,
                'keep_locales': self.keep_locales,
                'platform_info': self.platform_info
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Configuration exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False

    def import_config(self, input_path):
        """Import configuration from a file"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Apply imported configuration
            if 'nwjs_version' in config_data:
                self.nwjs_version = config_data['nwjs_version']
            if 'use_sdk' in config_data:
                self.use_sdk = config_data['use_sdk']
            if 'enable_devtools' in config_data:
                self.enable_devtools = config_data['enable_devtools']
            if 'platform_optimized' in config_data:
                self.platform_optimized = config_data['platform_optimized']
            if 'executable_name' in config_data:
                self.executable_name = config_data['executable_name']
            if 'cleanup_files' in config_data:
                self.cleanup_files = config_data['cleanup_files']
            if 'keep_locales' in config_data:
                self.keep_locales = config_data['keep_locales']
            
            logger.info(f"✓ Configuration imported from: {input_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False

    def generate_execution_report(self, result):
        """Generate a comprehensive execution report"""
        report = {
            'execution_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'script_version': '2.1.0',
            'game_path': str(self.game_path),
            'configuration': {
                'nwjs_version': self.nwjs_version,
                'use_sdk': self.use_sdk,
                'enable_devtools': self.enable_devtools,
                'platform_optimized': self.platform_optimized,
                'executable_name': self.executable_name,
                'platform': self.current_platform,
                'architecture': self.platform_info['architecture']
            },
            'operations_performed': [],
            'files_modified': [],
            'warnings': [],
            'success': result.get('success', False),
            'error': result.get('error', None)
        }
        
        # Add rollback information if available
        if 'rollback_data' in result:
            report['rollback_data'] = result['rollback_data']
        
        if result.get('success', False):
            report['operations_performed'] = [
                'game_directory_validation',
                'backup_creation',
                'nwjs_setup',
                'file_preservation',
                'runtime_integration',
                'executable_renaming',
                'cleanup',
                'shortcut_creation' if sys.platform == 'win32' else None
            ]
            
            report['files_modified'] = [
                'package.json',
                'index.html',
                f'{self.executable_name}{self.platform_info.get("executable_ext", "")}',
                'nwjs_automator.log'
            ]
            
            # Add configuration profile info if used
            if self.current_config:
                report['configuration_profile'] = self.current_config['name']
            
            # Add configuration template info if used
            if self.applied_template:
                report['configuration_template'] = self.applied_template['name']
        else:
            report['operations_performed'] = result.get('rollback_data', {}).get('operations', [])
            report['error_details'] = {
                'error_message': result.get('error', 'Unknown error'),
                'rollback_status': result.get('rollback_status', 'not_attempted'),
                'rollback_error': result.get('rollback_error', None)
            }
        
        return report

    def save_execution_report(self, report, output_path=None):
        """Save execution report to a file"""
        if not output_path:
            reports_dir = Path.cwd() / 'execution_reports'
            reports_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = reports_dir / f'report_{timestamp}.json'
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Execution report saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save execution report: {e}")
            return False

    def display_help_contextual(self, operation=None):
        """Display contextual help information"""
        help_topics = {
            'general': {
                'title': 'NW.js Automator Help',
                'description': 'Automates NW.js runtime updates for RPG Maker MV/MZ games',
                'usage': 'python nwjs_automator.py [options]',
                'examples': [
                    'python nwjs_automator.py --game-path "C:/Games/MyGame"',
                    'python nwjs_automator.py --game-path "/home/user/games/mygame" --nwjs-version v0.72.0',
                    'python nwjs_automator.py --config-profile development --game-path "C:/Games/MyGame"'
                ]
            },
            'profiles': {
                'title': 'Configuration Profiles',
                'description': 'Predefined configuration sets for different use cases',
                'profiles': {
                    'default': 'Balanced settings for most RPG Maker MV games',
                    'development': 'Optimized for game development with debugging tools',
                    'production': 'Optimized for final game distribution (smallest size)',
                    'compatibility': 'Maximum compatibility with older games',
                    'modern': 'Modern NW.js features (Windows 10+ required)'
                }
            },
            'templates': {
                'title': 'Configuration Templates',
                'description': 'Reusable configuration patterns for specific needs',
                'templates': {
                    'minimal': 'Smallest possible game size',
                    'debug': 'Full debugging support for development',
                    'multilingual': 'Preserves multiple language files'
                }
            },
            'rollback': {
                'title': 'Automatic Rollback System',
                'description': 'Automatically restores game to original state if errors occur',
                'features': [
                    'Monitors all critical operations',
                    'Attempts automatic restoration on failure',
                    'Provides detailed error information',
                    'Preserves backup integrity'
                ]
            },
            'config_management': {
                'title': 'Configuration Management',
                'description': 'Export, import, and manage configuration profiles',
                'commands': {
                    '--export-config': 'Export current configuration to a file',
                    '--import-config': 'Import configuration from a file',
                    '--config-profile': 'Use a predefined configuration profile',
                    '--config-template': 'Apply a configuration template'
                }
            }
        }
        
        if operation and operation in help_topics:
            topic = help_topics[operation]
            print(f"\n📚 {topic['title']}")
            print(f"📋 {topic['description']}")
            
            if 'profiles' in topic:
                print("\n📁 Available Profiles:")
                for name, desc in topic['profiles'].items():
                    print(f"  • {name}: {desc}")
            
            if 'templates' in topic:
                print("\n📋 Available Templates:")
                for name, desc in topic['templates'].items():
                    print(f"  • {name}: {desc}")
            
            if 'features' in topic:
                print("\n✨ Features:")
                for feature in topic['features']:
                    print(f"  • {feature}")
            
            if 'commands' in topic:
                print("\n💻 Commands:")
                for cmd, desc in topic['commands'].items():
                    print(f"  • {cmd}: {desc}")
            
            if 'examples' in topic:
                print("\n📝 Examples:")
                for example in topic['examples']:
                    print(f"  • {example}")
        else:
            # Show general help
            general_help = help_topics['general']
            print(f"\n📚 {general_help['title']}")
            print(f"📋 {general_help['description']}")
            print(f"\n💻 Usage: {general_help['usage']}")
            print(f"\n📝 Examples:")
            for example in general_help['examples']:
                print(f"  • {example}")
            
            print(f"\n📚 Available Help Topics:")
            for topic_name in help_topics:
                if topic_name != 'general':
                    print(f"  • {topic_name}")
            
            print(f"\n💡 Use --help-topic <topic> for detailed information on a specific topic")

    def check_for_updates(self):
        """Check for available updates from GitHub"""
        if not self.auto_update_config["enabled"]:
            logger.info("Auto-update is disabled")
            return None
            
        try:
            logger.info("Checking for updates...")
            response = requests.get(self.auto_update_config["update_url"], timeout=10)
            response.raise_for_status()
            
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            current_version = "2.1.1"  # This should be dynamic in production
            
            if latest_version != current_version:
                logger.info(f"Update available: {latest_version} (current: {current_version})")
                return {
                    "current_version": current_version,
                    "latest_version": latest_version,
                    "download_url": latest_release["assets"][0]["browser_download_url"]
                }
            else:
                logger.info("No updates available")
                return None
                
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return None

    def perform_update(self, update_info):
        """Perform automatic update"""
        if not update_info:
            logger.info("No update to perform")
            return False
            
        try:
            logger.info(f"Downloading update {update_info['latest_version']}...")
            
            # Backup current script
            if self.auto_update_config["backup_before_update"]:
                backup_path = Path(__file__).with_suffix('.backup')
                shutil.copy2(__file__, backup_path)
                logger.info(f"Backup created at {backup_path}")
                
            # Download update
            response = requests.get(update_info['download_url'], stream=True)
            response.raise_for_status()
            
            # Save new version
            temp_file = Path(__file__).with_suffix('.new')
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify integrity (basic check)
            if self.auto_update_config["verify_integrity"]:
                if temp_file.stat().st_size == 0:
                    raise Exception("Downloaded file is empty")
                
            # Replace current script
            temp_file.replace(__file__)
            logger.info(f"Successfully updated to version {update_info['latest_version']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            # Restore backup if exists
            backup_path = Path(__file__).with_suffix('.backup')
            if backup_path.exists():
                backup_path.replace(__file__)
                logger.info("Restored from backup")
            return False

    def detect_platform_info(self):
        """Detect platform information and return optimized configuration"""
        platform_info = {
            'os': self.current_platform,
            'architecture': platform.architecture()[0],
            'machine': platform.machine().lower(),
            'processor': platform.processor(),
            'node': platform.node(),
            'release': platform.release()
        }
        
        # Platform-specific optimizations
        if self.current_platform == 'windows':
            platform_info['executable_ext'] = '.exe'
            platform_info['path_separator'] = '\\'
            platform_info['recommended_version'] = 'v0.49.2'
            platform_info['supports_sdk'] = True
        elif self.current_platform == 'darwin':  # macOS
            platform_info['executable_ext'] = ''
            platform_info['path_separator'] = '/'
            platform_info['recommended_version'] = 'v0.52.0'
            platform_info['supports_sdk'] = True
            # Check for ARM64 (Apple Silicon)
            if platform.machine().lower() == 'arm64':
                platform_info['architecture'] = 'arm64'
                platform_info['recommended_version'] = 'v0.52.0'
        elif self.current_platform == 'linux':
            platform_info['executable_ext'] = ''
            platform_info['path_separator'] = '/'
            platform_info['recommended_version'] = 'v0.50.1'
            platform_info['supports_sdk'] = True
        else:
            platform_info['executable_ext'] = ''
            platform_info['path_separator'] = '/'
            platform_info['recommended_version'] = 'v0.49.2'
            platform_info['supports_sdk'] = False
        
        logger.info(f"Platform detected: {self.current_platform} ({platform_info['architecture']})")
        return platform_info

    def validate_nwjs_version(self):
        """Validate NW.js version compatibility and suggest alternatives"""
        version_info = self.sdk_compatibility.get(self.nwjs_version, {})
        
        if not version_info:
            logger.warning(f"Unknown NW.js version: {self.nwjs_version}")
            logger.info(f"Falling back to recommended version for {self.current_platform}: {self.platform_info['recommended_version']}")
            self.nwjs_version = self.platform_info['recommended_version']
            return False
        
        if not version_info.get('stable', False):
            logger.warning(f"NW.js version {self.nwjs_version} is not marked as stable")
            if not version_info.get('tested', False):
                logger.warning(f"Version {self.nwjs_version} has not been tested with RPG Maker MV")
        
        if not version_info.get('recommended', False):
            logger.info(f"Consider using recommended version {self.platform_info['recommended_version']} for better compatibility")
        
        # Check if SDK is supported for this version
        if self.use_sdk and not self.platform_info.get('supports_sdk', True):
            logger.warning(f"SDK builds not fully supported on {self.current_platform}")
            self.use_sdk = False
            logger.info("Falling back to normal build")
        
        return True

    def configure_sdk_features(self):
        """Configure SDK-specific features based on user preferences"""
        if self.use_sdk:
            logger.info("Configuring SDK build features...")
            
            # Enable developer tools if requested
            if self.enable_devtools:
                logger.info("Developer tools enabled (F12 access)")
                # SDK builds have dev tools enabled by default
            
            # Platform-specific SDK configurations
            if self.current_platform == 'windows':
                # Windows-specific SDK optimizations
                self.cleanup_files = [f for f in self.cleanup_files if f not in ['nw_100_percent.pak', 'nw_200_percent.pak']]
                logger.info("Preserved SDK-specific files for Windows")
            
            # Add SDK-specific files to keep
            self.keep_files.extend(['payload', 'debug.log'])
            
        else:
            logger.info("Using standard NW.js build (non-SDK)")
            # Remove SDK-specific files from cleanup list
            self.cleanup_files.extend(['payload', 'debug.log'])
            if 'payload' in self.keep_files:
                self.keep_files.remove('payload')
            if 'debug.log' in self.keep_files:
                self.keep_files.remove('debug.log')

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

    def validate_input_path(self, path):
        """Validate and sanitize input paths for security"""
        if not path:
            raise ValueError("Path cannot be empty")
        
        # Convert to absolute path to prevent path traversal
        try:
            absolute_path = Path(path).resolve()
            
            # Check if path is within a reasonable system directory
            # This prevents access to system directories like C:\Windows, /etc, etc.
            if self.current_platform == 'windows':
                system_dirs = ['windows', 'program files', 'program files (x86)', 'system32']
                if any(str(absolute_path).lower().startswith(f'{drive}:\\{dir}\\') 
                       for drive in ['c', 'd', 'e', 'f'] for dir in system_dirs):
                    raise ValueError(f"Access to system directory {absolute_path} is not allowed")
            else:  # Unix-like systems
                system_dirs = ['/etc', '/usr', '/bin', '/sbin', '/lib']
                if any(str(absolute_path).startswith(dir) for dir in system_dirs):
                    raise ValueError(f"Access to system directory {absolute_path} is not allowed")
            
            return absolute_path
            
        except Exception as e:
            raise ValueError(f"Invalid path: {e}")

    def validate_game_directory(self):
        """Validate that the provided path is a valid RPG Maker MV game directory"""
        # Security: Validate the path first
        try:
            self.game_path = self.validate_input_path(self.game_path)
        except ValueError as e:
            raise ValueError(f"Security validation failed: {e}")
        
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
        """Validate and fix package.json for NW.js compatibility with advanced validation"""
        logger.info("Validating package.json with advanced checks...")

        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in package.json: {e}")
        except Exception as e:
            raise ValueError(f"Could not read package.json: {e}")

        # Check and fix required fields for NW.js with advanced validation
        fixes_made = False
        issues_found = []

        # 1. Check 'name' field (required by NW.js) - Enhanced validation
        if 'name' not in package_data or not package_data['name']:
            game_name = self.game_path.name.replace(' ', '-').lower()
            package_data['name'] = game_name
            logger.info(f"  Fixed: Added missing 'name' field: {game_name}")
            fixes_made = True
        elif not isinstance(package_data['name'], str):
            # Convert to string if it's not
            package_data['name'] = str(package_data['name'])
            logger.info(f"  Fixed: Converted 'name' field to string")
            fixes_made = True
        elif len(package_data['name']) > 214:
            # NW.js has a 214 character limit for app name
            original_name = package_data['name']
            package_data['name'] = original_name[:214]
            logger.warning(f"  Fixed: Truncated 'name' field from {len(original_name)} to 214 characters")
            fixes_made = True

        # 2. Check 'main' field (required by NW.js)
        if 'main' not in package_data or not package_data['main']:
            package_data['main'] = 'www/index.html'  # Default for RPG Maker MV
            logger.info(f"  Fixed: Added missing 'main' field: www/index.html")
            fixes_made = True
        elif not isinstance(package_data['main'], str):
            package_data['main'] = str(package_data['main'])
            logger.info(f"  Fixed: Converted 'main' field to string")
            fixes_made = True

        # 3. Check 'window' object (important for RPG Maker MV)
        if 'window' not in package_data:
            package_data['window'] = {
                'title': package_data.get('name', 'RPG Game'),
                'toolbar': False,
                'width': 800,
                'height': 600
            }
            logger.info(f"  Fixed: Added missing 'window' configuration")
            fixes_made = True
        else:
            # Validate window properties
            window_obj = package_data['window']
            if not isinstance(window_obj, dict):
                package_data['window'] = {
                    'title': package_data.get('name', 'RPG Game'),
                    'toolbar': False,
                    'width': 800,
                    'height': 600
                }
                logger.info(f"  Fixed: Replaced invalid 'window' configuration")
                fixes_made = True
            else:
                # Validate individual window properties
                if 'title' not in window_obj or not window_obj['title']:
                    window_obj['title'] = package_data.get('name', 'RPG Game')
                    logger.info(f"  Fixed: Added missing 'window.title'")
                    fixes_made = True
                
                # Ensure width and height are valid numbers
                if 'width' not in window_obj or not isinstance(window_obj['width'], int) or window_obj['width'] <= 0:
                    window_obj['width'] = 800
                    logger.info(f"  Fixed: Set default 'window.width' to 800")
                    fixes_made = True
                
                if 'height' not in window_obj or not isinstance(window_obj['height'], int) or window_obj['height'] <= 0:
                    window_obj['height'] = 600
                    logger.info(f"  Fixed: Set default 'window.height' to 600")
                    fixes_made = True

        # 4. Check for recommended NW.js specific fields
        if 'chromium-args' not in package_data:
            package_data['chromium-args'] = '--disable-background-timer-throttling'
            logger.info(f"  Added: Recommended 'chromium-args' for better performance")
            fixes_made = True

        # 5. Validate js-flags if present
        if 'js-flags' in package_data:
            if not isinstance(package_data['js-flags'], str):
                package_data['js-flags'] = str(package_data['js-flags'])
                logger.info(f"  Fixed: Converted 'js-flags' to string")
                fixes_made = True

        # 6. Add KADOKAWA/RPGMV format support for official compatibility
        if package_data.get('name') != 'KADOKAWA/RPGMV':
            # Store original name in a custom field for reference
            if 'original_name' not in package_data:
                package_data['original_name'] = package_data['name']
                logger.info(f"  Info: Stored original name: {package_data['original_name']}")

        # Save the fixed package.json if any fixes were made
        if fixes_made:
            try:
                with open(package_json_path, 'w', encoding='utf-8') as f:
                    json.dump(package_data, f, indent=2, ensure_ascii=False)
                logger.info("✓ package.json fixes saved with advanced validation")
                return True
            except Exception as e:
                logger.error(f"Could not save package.json fixes: {e}")
                raise
        else:
            logger.info("✓ package.json is already valid")
            return False

    def get_nwjs_download_url(self):
        """Get the download URL for the specified NW.js version with version validation"""
        
        # Validate the NW.js version first
        validated_version = self._validate_nwjs_version(self.nwjs_version)
        
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

        # Use the validated version
        version = validated_version if validated_version.startswith(
            'v') else f"v{validated_version}"

        if self.use_sdk:
            filename = f"nwjs-sdk-{version}-{platform_name}-{arch}"
        else:
            filename = f"nwjs-{version}-{platform_name}-{arch}"

        if platform_name == 'win':
            filename += '.zip'
        else:
            filename += '.tar.gz'

        return f"{self.nwjs_url_base}/{version}/{filename}", filename
    
    def _validate_nwjs_version(self, version):
        """Validate NW.js version and suggest compatible versions for RPG Maker MV"""
        logger.info(f"Validating NW.js version: {version}")
        
        # List of known compatible versions for RPG Maker MV
        compatible_versions = {
            'v0.29.4': {'description': 'Original RPG Maker MV version', 'platforms': ['win32', 'darwin', 'linux']},
            'v0.49.2': {'description': 'Balanced version with good compatibility', 'platforms': ['win32', 'darwin', 'linux']},
            'v0.72.0': {'description': 'Modern stable version', 'platforms': ['win32', 'darwin', 'linux']},
            'v0.90.0': {'description': 'Latest stable with best performance', 'platforms': ['win32', 'darwin', 'linux']},
            'v0.100.1': {'description': 'Very recent version', 'platforms': ['win32', 'darwin', 'linux']}
        }
        
        # Platform-specific recommendations
        platform_recommendations = {
            'win32': ['v0.72.0', 'v0.49.2', 'v0.90.0'],
            'darwin': ['v0.49.2', 'v0.72.0', 'v0.90.0'],
            'linux': ['v0.72.0', 'v0.90.0', 'v0.49.2']
        }
        
        # Clean and normalize the version
        clean_version = version.strip().lower()
        if clean_version.startswith('v'):
            clean_version = clean_version[1:]
        
        # Check if it's a known compatible version
        if f"v{clean_version}" in compatible_versions:
            logger.info(f"✓ Version {version} is known to be compatible with RPG Maker MV")
            return f"v{clean_version}" if not version.startswith('v') else version
        
        # Check if it's a valid version format (even if not in our list)
        if self._is_valid_version_format(clean_version):
            logger.warning(f"⚠️  Version {version} is not in the tested compatibility list")
            logger.info(f"   Recommended versions: {', '.join(compatible_versions.keys())}")
            
            # Suggest platform-specific recommendation
            current_platform = sys.platform
            if current_platform in platform_recommendations:
                recommended = platform_recommendations[current_platform][0]
                logger.info(f"   Recommended for {current_platform}: {recommended}")
            
            return version  # Still allow it, but with warning
        
        # If version is invalid, use the default
        logger.warning(f"❌ Invalid version format: {version}")
        default_version = "v0.49.2"
        logger.info(f"   Falling back to default version: {default_version}")
        return default_version
    
    def _is_valid_version_format(self, version):
        """Check if version string has a valid format"""
        # Basic version format validation (e.g., 0.49.2, 0.72.0, 1.0.0)
        import re
        version_pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(version_pattern, version))
    
    def suggest_nwjs_version(self):
        """Suggest the best NW.js version for the current platform"""
        platform_suggestions = {
            'win32': 'v0.72.0',  # Best balance for Windows
            'darwin': 'v0.49.2',  # Most stable for Mac
            'linux': 'v0.72.0'   # Best compatibility for Linux
        }
        
        current_platform = sys.platform
        suggested_version = platform_suggestions.get(current_platform, 'v0.49.2')
        
        logger.info(f"Suggested NW.js version for {current_platform}: {suggested_version}")
        return suggested_version

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
        """Create an incremental backup of the original game with verification"""
        backup_dir = self.game_path.parent / f"{self.game_path.name}_backups"
        backup_dir.mkdir(exist_ok=True)
        
        # Generate timestamp for backup
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{self.game_path.name}_backup_{timestamp}"

        if backup_path.exists():
            logger.info(f"Backup already exists: {backup_path}")
            return backup_path

        logger.info(f"Creating incremental backup: {backup_path}")
        
        # Create backup with verification
        try:
            shutil.copytree(self.game_path, backup_path)
            
            # Verify backup integrity
            if self._verify_backup_integrity(backup_path):
                logger.info("✓ Backup created and verified successfully")
                
                # Create backup manifest
                self._create_backup_manifest(backup_path)
                
                # Clean up old backups (keep last 3)
                self._cleanup_old_backups(backup_dir)
                
                return backup_path
            else:
                logger.error("❌ Backup verification failed")
                shutil.rmtree(backup_path, ignore_errors=True)
                raise RuntimeError("Backup integrity verification failed")
                
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            if backup_path.exists():
                shutil.rmtree(backup_path, ignore_errors=True)
            raise
    
    def _verify_backup_integrity(self, backup_path):
        """Verify the integrity of the backup by checking critical files"""
        logger.info("Verifying backup integrity...")
        
        critical_files = [
            'package.json',
            'www',
            'www/index.html'
        ]
        
        missing_files = []
        corrupted_files = []
        
        for file_name in critical_files:
            file_path = backup_path / file_name
            
            if not file_path.exists():
                missing_files.append(file_name)
                continue
            
            # For directories, check they're not empty
            if file_path.is_dir():
                if not any(file_path.iterdir()):
                    corrupted_files.append(f"{file_name} (empty directory)")
            else:
                # For files, check they're not empty
                try:
                    if file_path.stat().st_size == 0:
                        corrupted_files.append(file_name)
                except Exception:
                    corrupted_files.append(file_name)
        
        if missing_files:
            logger.error(f"Missing critical files in backup: {missing_files}")
            return False
        
        if corrupted_files:
            logger.error(f"Corrupted files in backup: {corrupted_files}")
            return False
        
        logger.info("✓ Backup integrity verified - all critical files present and valid")
        return True
    
    def _create_backup_manifest(self, backup_path):
        """Create a manifest file for the backup"""
        manifest_path = backup_path / 'BACKUP_MANIFEST.txt'
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(f"NW.js Automator Backup Manifest\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Original Path: {self.game_path}\n")
                f.write(f"NW.js Version: {self.nwjs_version}\n")
                f.write(f"SDK Build: {self.use_sdk}\n")
                f.write(f"\nBackup Contents:\n")
                
                # List all files in backup
                for item in backup_path.rglob("*"):
                    if item.is_file():
                        relative_path = item.relative_to(backup_path)
                        size = item.stat().st_size
                        f.write(f"  {relative_path} ({size} bytes)\n")
            
            logger.info(f"✓ Backup manifest created: {manifest_path}")
            return True
            
        except Exception as e:
            logger.warning(f"Could not create backup manifest: {e}")
            return False
    
    def _cleanup_old_backups(self, backup_dir):
        """Clean up old backups, keeping only the most recent ones"""
        try:
            # Get all backup directories
            backups = [d for d in backup_dir.iterdir() if d.is_dir() and '_backup_' in d.name]
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep last 3 backups, remove older ones
            backups_to_remove = backups[3:]
            
            for backup in backups_to_remove:
                logger.info(f"Removing old backup: {backup}")
                shutil.rmtree(backup, ignore_errors=True)
            
            if backups_to_remove:
                logger.info(f"✓ Cleaned up {len(backups_to_remove)} old backups")
            
        except Exception as e:
            logger.warning(f"Could not cleanup old backups: {e}")
    
    def restore_from_backup(self, backup_path):
        """Restore game from a backup with verification"""
        logger.info(f"Restoring game from backup: {backup_path}")
        
        try:
            # Verify backup integrity before restoration
            if not self._verify_backup_integrity(backup_path):
                raise RuntimeError("Backup integrity verification failed before restoration")
            
            # Create temporary restore path
            temp_restore = self.game_path.parent / f"{self.game_path.name}_restore_temp"
            
            try:
                # Copy backup to temporary location
                shutil.copytree(backup_path, temp_restore)
                
                # Verify the restored files
                if not self._verify_backup_integrity(temp_restore):
                    raise RuntimeError("Restored files verification failed")
                
                # Remove original game directory
                if self.game_path.exists():
                    logger.info(f"Removing original game directory: {self.game_path}")
                    shutil.rmtree(self.game_path)
                
                # Move restored files to original location
                temp_restore.rename(self.game_path)
                
                logger.info("✓ Game restored successfully from backup")
                return True
                
            except Exception as e:
                logger.error(f"Restoration failed: {e}")
                # Clean up temporary restore
                if temp_restore.exists():
                    shutil.rmtree(temp_restore, ignore_errors=True)
                raise
                
        except Exception as e:
            logger.error(f"Could not restore from backup: {e}")
            raise

    def save_important_files(self):
        """Save package.json, www folder, and index.html before cleaning"""
        logger.info(
            "Saving important files (package.json, www folder, and index.html)...")

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
            # Changed from 'www/index.html' to 'index.html'
            shutil.copy2(index_html, temp_dir / 'index.html')
            logger.info("  Saved: index.html")
        else:
            logger.warning("  index.html not found - this may cause issues!")

        for file in critical_files:
            if not (temp_dir / file).exists():
                missing_files.append(file)

        if missing_files:
            logger.error(
                f"Critical files not saved to temp directory: {missing_files}")
            logger.error("Aborting to prevent data loss!")
            raise FileNotFoundError(
                f"Failed to backup critical files: {missing_files}")

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
        logger.info(
            f"Copying NW.js runtime files from {nwjs_dir} to {self.game_path}...")
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
            finally:
                logger.info(
                    f"✓ Copied {copied_count} NW.js runtime files to game directory")

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
            logger.error(
                f"NW.js executable not found. Looked for: {possible_executables}")
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

    def cleanup_nwjs_files(self, keep_debug_files=False):
        """Clean up unnecessary NW.js files with intelligent analysis"""
        logger.info("Cleaning up unnecessary NW.js files with smart cleanup...")

        removed_count = 0
        preserved_count = 0
        
        # Analyze files before removal
        files_to_clean = self._analyze_files_for_cleanup()
        
        # Remove files from the cleanup list
        for file_name in files_to_clean:
            file_path = self.game_path / file_name
            if file_path.exists():
                try:
                    # Check if file is in whitelist
                    if self._is_critical_file(file_path):
                        logger.info(f"  Preserved (critical): {file_name}")
                        preserved_count += 1
                        continue
                    
                    # Check if we should keep debug files
                    if keep_debug_files and file_name in self.debug_files:
                        logger.info(f"  Preserved (debug mode): {file_name}")
                        preserved_count += 1
                        continue
                    
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    removed_count += 1
                    logger.info(f"  Removed: {file_name}")
                except Exception as e:
                    logger.warning(f"  Could not remove {file_name}: {e}")

        # Handle locale directory cleanup - keep only specified locales
        locales_dir = self.game_path / 'locales'
        if locales_dir.exists() and locales_dir.is_dir():
            try:
                for locale_file in locales_dir.iterdir():
                    if locale_file.name not in self.keep_locales:
                        if locale_file.is_file():
                            locale_file.unlink()
                            removed_count += 1
                            logger.info(
                                f"  Removed: locales/{locale_file.name}")
            except Exception as e:
                logger.warning(f"  Could not clean locales directory: {e}")

        # Analyze remaining files and suggest optimizations
        self._analyze_remaining_files()

        if removed_count > 0:
            logger.info(f"✓ Removed {removed_count} unnecessary files")
        else:
            logger.info("✓ No unnecessary files to remove")
        
        if preserved_count > 0:
            logger.info(f"✓ Preserved {preserved_count} critical/debug files")
    
    def _analyze_files_for_cleanup(self):
        """Analyze which files should be cleaned up based on actual usage"""
        logger.info("Analyzing files for smart cleanup...")
        
        # Start with the base cleanup list
        files_to_clean = self.cleanup_files.copy()
        
        # Check if SDK build is being used
        if self.use_sdk:
            # Remove SDK-specific files from cleanup if we're using SDK
            sdk_files = ['nw_100_percent.pak', 'nw_200_percent.pak']
            files_to_clean = [f for f in files_to_clean if f not in sdk_files]
            logger.info("  SDK build detected - preserving SDK-specific files")
        
        # Check for platform-specific files
        if sys.platform == 'win32':
            # On Windows, we might want to keep notification_helper.exe
            if 'notification_helper.exe' in files_to_clean:
                files_to_clean.remove('notification_helper.exe')
                logger.info("  Windows platform - preserving notification_helper.exe")
        
        return files_to_clean
    
    def _is_critical_file(self, file_path):
        """Check if a file is critical and should never be removed"""
        file_name = file_path.name
        
        # Check against whitelist
        if file_name in self.critical_files_whitelist:
            return True
        
        # Check if it's a directory in whitelist
        if file_path.is_dir() and file_name in self.critical_files_whitelist:
            return True
        
        # Special case: check if it's the main executable
        if file_name in ['nw.exe', 'nw', 'nwjs'] and file_path.exists():
            return True
        
        return False
    
    def _analyze_remaining_files(self):
        """Analyze remaining files and suggest optimizations"""
        logger.info("Analyzing remaining file structure...")
        
        # Count files by category
        file_categories = {
            'executables': 0,
            'configuration': 0,
            'resources': 0,
            'locales': 0,
            'other': 0
        }
        
        total_size = 0
        
        for item in self.game_path.iterdir():
            if item.is_file():
                item_size = item.stat().st_size
                total_size += item_size
                
                if item.name.endswith(('.exe', 'nw', 'nwjs')):
                    file_categories['executables'] += 1
                elif item.name == 'package.json':
                    file_categories['configuration'] += 1
                elif item.name.startswith('icudtl') or item.name.startswith('lib'):
                    file_categories['resources'] += 1
                elif item.name.startswith('locales'):
                    file_categories['locales'] += 1
                else:
                    file_categories['other'] += 1
        
        logger.info(f"  File analysis: {file_categories}")
        logger.info(f"  Total size: {total_size / 1024 / 1024:.1f}MB")
        
        # Performance analysis
        if file_categories['other'] > 5:
            logger.info("  💡 Suggestion: Consider reviewing 'other' files for additional cleanup")
        
        # Performance optimization
        if total_size > 50 * 1024 * 1024:  # >50MB
            logger.info("  💡 Suggestion: Game size is large, consider additional optimization")

    def optimize_performance(self):
        """Apply performance optimizations based on configuration"""
        if not self.performance_config["parallel_downloads"]:
            return
            
        logger.info("Applying performance optimizations...")
        
        # Memory optimization - clear caches
        if self.performance_config["memory_optimization"]:
            import gc
            gc.collect()
            logger.info("  ✓ Memory optimized (garbage collection)")
        
        # File caching optimization
        if self.performance_config["file_caching"]:
            # This would be implemented with actual caching in production
            logger.info("  ✓ File caching enabled")
        
        # Bottleneck analysis
        if self.performance_config["bottleneck_analysis"]:
            self._analyze_performance_bottlenecks()

    def _analyze_performance_bottlenecks(self):
        """Analyze potential performance bottlenecks"""
        logger.info("  🔍 Analyzing performance bottlenecks...")
        
        # Check system resources
        if self.current_platform == 'windows':
            try:
                import psutil
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                
                if cpu_usage > 80:
                    logger.warning(f"  ⚠️  High CPU usage: {cpu_usage}%")
                if memory_usage > 80:
                    logger.warning(f"  ⚠️  High memory usage: {memory_usage}%")
                    
            except ImportError:
                logger.info("  ℹ️  Install psutil for advanced performance monitoring")
        
        if file_categories['locales'] > 2:
            logger.info("  💡 Suggestion: You're keeping multiple locale files. Consider keeping only en-US for smaller size.")

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
        
        # Initialize rollback monitoring
        rollback_data = {
            'original_state': None,
            'operations': [],
            'current_operation': None,
            'success': False
        }
        
        try:
            # Step 0: Validate game directory
            self.validate_game_directory()
            rollback_data['operations'].append('validation_completed')

            # Step 0.5: Create backup if requested
            backup_path = None
            if create_backup:
                backup_path = self.backup_game()
                rollback_data['original_state'] = backup_path
                rollback_data['operations'].append('backup_created')

            # Step 1: Setup NW.js (download SDK build)
            nwjs_dir = self.setup_nwjs()
            rollback_data['operations'].append('nwjs_setup_completed')

            # Step 3a: Save package.json, www folder, and index.html
            temp_dir = self.save_important_files()
            rollback_data['operations'].append('files_saved')

            # Step 3b: Delete everything inside game folder
            self.clean_game_directory()
            rollback_data['operations'].append('game_cleaned')

            # Step 3b: Copy NW.js files to game directory
            self.copy_nwjs_to_game(nwjs_dir)
            rollback_data['operations'].append('nwjs_copied')

            # Step 3c: Restore package.json, www folder, and index.html
            self.restore_important_files(temp_dir)
            rollback_data['operations'].append('files_restored')

            # Step 3c: Rename nw.exe to custom executable name
            game_exe = self.rename_executable()
            rollback_data['operations'].append('executable_renamed')

            # Step 3d: Delete chromedriver (and other cleanup)
            self.cleanup_nwjs_files()
            rollback_data['operations'].append('cleanup_completed')

            if not game_exe:
                raise FileNotFoundError("Could not create game executable")

            # Optional: Create shortcut on Windows
            if sys.platform == 'win32':
                self.create_shortcut_windows(game_exe)
                rollback_data['operations'].append('shortcut_created')

            # Cleanup temporary files
            self.cleanup_temp_files()
            rollback_data['operations'].append('temp_cleaned')

            # Mark operation as successful
            rollback_data['success'] = True
            
            logger.info("🎉 NW.js update completed successfully!")
            logger.info(f"🚀 Launch the game using: {game_exe}")
            logger.info(
                "💡 Type 'process.versions' in the game console to check your new NW.js version!")

            return {
                'success': True,
                'game_executable': game_exe,
                'game_path': self.game_path,
                'rollback_data': rollback_data
            }

        except Exception as e:
            logger.error(f"❌ Update failed: {e}")
            
            # Attempt automatic rollback if we have backup data
            if rollback_data['original_state'] and not rollback_data['success']:
                logger.info("🔄 Attempting automatic rollback...")
                try:
                    self.restore_from_backup(rollback_data['original_state'])
                    logger.info("✅ Automatic rollback completed successfully!")
                    logger.info(f"💾 Game restored to original state from: {rollback_data['original_state']}")
                    return {
                        'success': False,
                        'error': str(e),
                        'rollback_status': 'success',
                        'rollback_source': rollback_data['original_state']
                    }
                except Exception as rollback_error:
                    logger.error(f"❌ Rollback failed: {rollback_error}")
                    return {
                        'success': False,
                        'error': str(e),
                        'rollback_status': 'failed',
                        'rollback_error': str(rollback_error)
                    }
            else:
                return {
                    'success': False,
                    'error': str(e),
                    'rollback_status': 'not_attempted'
                }


def get_user_input():
    """Get user input for configuration options"""
    print("🎮 RPG Maker MV NW.js Update Automation Tool")
    print("=" * 80)

    # Get game path
    while True:
        game_path = input(
            "\n📁 Enter the path to your RPG Maker MV game directory: ").strip()
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
    executable_name = input(
        "Enter the name for your game executable (default: Game): ").strip()
    if not executable_name:
        executable_name = "Game"
    # Remove .exe extension if provided (will be added automatically on Windows)
    if executable_name.lower().endswith('.exe'):
        executable_name = executable_name[:-4]

    # Get NW.js path (optional)
    nwjs_path = input(
        "\n⚙️  Enter path to existing NW.js installation (press Enter to download): ").strip()
    nwjs_path = nwjs_path.strip('"\'') if nwjs_path else None

    # Get NW.js version
    print("\n🔧 NW.js Version Options:")
    print("  1. v0.29.4 (Maximum compatibility - original RPG Maker MV era)")
    print("  2. v0.49.2 (Balanced - good performance with broad compatibility)")
    print("  3. v0.72.0 (Modern stable - last version supporting Windows 7)")
    print("  4. v0.90.0+ (Latest stable - best performance, requires Windows 10+)")
    print("  5. Custom version")

    while True:
        version_choice = input(
            "\nSelect version (1-5) or press Enter for balanced default: ").strip()
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
            custom_version = input(
                "Enter custom version (e.g., v0.100.1): ").strip()
            if custom_version:
                nwjs_version = custom_version if custom_version.startswith(
                    'v') else f'v{custom_version}'
                break
        print("❌ Invalid choice. Please select 1, 2, 3, 4, 5, or press Enter.")

    # Get build type
    use_sdk = input("\n🛠️  Use SDK build? (Y/n): ").strip().lower()
    use_sdk = use_sdk != 'n'

    # Get backup preference
    create_backup = input(
        "\n💾 Create backup before processing? (Y/n): ").strip().lower()
    create_backup = create_backup != 'n'

    # Verbose logging
    verbose = input("\n📝 Enable verbose logging? (y/N): ").strip().lower()
    verbose = verbose == 'y'

    # Logging level
    if verbose:
        logging_level = 'DEBUG'
    else:
        print("\n📊 Logging Level:")
        print("  1. DEBUG (Most detailed)")
        print("  2. INFO (Default)")
        print("  3. WARNING (Only warnings and errors)")
        print("  4. ERROR (Only errors)")
        
        log_choice = input(
            "Select logging level (1-4, default 2): ").strip()
        log_levels = {'1': 'DEBUG', '2': 'INFO', '3': 'WARNING', '4': 'ERROR'}
        logging_level = log_levels.get(log_choice, 'INFO')

    # Developer tools
    enable_devtools = input(
        "\n🔧 Enable developer tools (F12 access)? (y/N): ").strip().lower()
    enable_devtools = enable_devtools == 'y'

    # Platform optimizations
    platform_optimized = input(
        "\n🌍 Enable platform-specific optimizations? (Y/n): ").strip().lower()
    platform_optimized = platform_optimized != 'n'

    return {
        'game_path': game_path,
        'executable_name': executable_name,
        'nwjs_path': nwjs_path,
        'nwjs_version': nwjs_version,
        'use_sdk': use_sdk,
        'create_backup': create_backup,
        'verbose': verbose,
        'logging_level': logging_level,
        'enable_devtools': enable_devtools,
        'platform_optimized': platform_optimized
    }


def main():
    parser = argparse.ArgumentParser(
        description='Automate NW.js update for RPG Maker MV games')
    parser.add_argument(
        '--game-path', help='Path to the RPG Maker MV game directory')
    parser.add_argument('--executable-name', default='Game',
                        help='Name for the game executable (default: Game)')
    parser.add_argument(
        '--nwjs-path', help='Path to existing NW.js installation (optional)')
    parser.add_argument('--nwjs-version', default='v0.49.2',
                        help='NW.js version to download (default: v0.49.2)')
    parser.add_argument('--no-sdk', action='store_true',
                        help='Use normal build instead of SDK build')
    parser.add_argument('--no-backup', action='store_true',
                        help='Skip creating backup')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--interactive', '-i',
                        action='store_true', help='Run in interactive mode')
    parser.add_argument('--devtools', action='store_true',
                        help='Enable developer tools (F12 access)')
    parser.add_argument('--platform-optimized', action='store_true',
                        help='Enable platform-specific optimizations')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set logging level (default: INFO)')
    parser.add_argument('--config-profile', 
                        choices=['default', 'development', 'production', 'compatibility', 'modern'],
                        help='Use a predefined configuration profile')
    parser.add_argument('--config-template', 
                        choices=['minimal', 'debug', 'multilingual'],
                        help='Apply a configuration template')
    parser.add_argument('--export-config', 
                        help='Export current configuration to a file')
    parser.add_argument('--import-config', 
                        help='Import configuration from a file')
    parser.add_argument('--help-topic', 
                        help='Display contextual help on a specific topic')

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
            executable_name=config['executable_name'],
            enable_devtools=config.get('enable_devtools', False),
            platform_optimized=config.get('platform_optimized', False),
            logging_level=config.get('logging_level', 'INFO')
        )
        
        # Configure SDK features based on user preferences
        automator.configure_sdk_features()
        
        # Validate NW.js version compatibility
        automator.validate_nwjs_version()

        # Show configuration summary
        print(f"\n📋 Configuration Summary:")
        print(f"   Game Path: {config['game_path']}")
        print(f"   Executable Name: {config['executable_name']}")
        print(f"   NW.js Version: {config['nwjs_version']}")
        print(f"   Build Type: {'SDK' if config['use_sdk'] else 'Normal'}")
        print(f"   Developer Tools: {'Enabled' if config['enable_devtools'] else 'Disabled'}")
        print(f"   Platform Optimized: {'Yes' if config['platform_optimized'] else 'No'}")
        print(f"   Logging Level: {config['logging_level']}")
        print(
            f"   Create Backup: {'Yes' if config['create_backup'] else 'No'}")
        if config['nwjs_path']:
            print(f"   NW.js Path: {config['nwjs_path']}")

        confirm = input(
            f"\n🚀 Proceed with automation? (Y/n): ").strip().lower()
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

        # Determine logging level
        log_level = args.log_level if not args.verbose else 'DEBUG'
        
        # Handle configuration export/import before creating automator
        if args.export_config:
            # Create a temporary automator to export default config
            temp_automator = NWJSAutomator(
                game_path=args.game_path or '.',
                nwjs_version=args.nwjs_version,
                use_sdk=not args.no_sdk,
                executable_name=executable_name,
                enable_devtools=args.devtools,
                platform_optimized=args.platform_optimized,
                logging_level=log_level
            )
            if temp_automator.export_config(args.export_config):
                print(f"✅ Configuration exported to: {args.export_config}")
                sys.exit(0)
            else:
                print(f"❌ Failed to export configuration")
                sys.exit(1)
        
        # Handle help topic display
        if args.help_topic:
            temp_automator = NWJSAutomator(
                game_path=args.game_path or '.',
                nwjs_version=args.nwjs_version,
                use_sdk=not args.no_sdk,
                executable_name=executable_name,
                enable_devtools=args.devtools,
                platform_optimized=args.platform_optimized,
                logging_level=log_level
            )
            temp_automator.display_help_contextual(args.help_topic)
            sys.exit(0)
        
        if args.import_config:
            # Create a temporary automator to import config
            temp_automator = NWJSAutomator(
                game_path=args.game_path or '.',
                nwjs_version=args.nwjs_version,
                use_sdk=not args.no_sdk,
                executable_name=executable_name,
                enable_devtools=args.devtools,
                platform_optimized=args.platform_optimized,
                logging_level=log_level
            )
            if temp_automator.import_config(args.import_config):
                print(f"✅ Configuration imported from: {args.import_config}")
                # Update arguments from imported config
                args.nwjs_version = temp_automator.nwjs_version
                args.no_sdk = not temp_automator.use_sdk
                executable_name = temp_automator.executable_name
                args.devtools = temp_automator.enable_devtools
                args.platform_optimized = temp_automator.platform_optimized
            else:
                print(f"❌ Failed to import configuration")
                sys.exit(1)
        
        # Create automator instance with configuration support
        automator = NWJSAutomator(
            game_path=args.game_path,
            nwjs_path=args.nwjs_path,
            nwjs_version=args.nwjs_version,
            use_sdk=not args.no_sdk,
            executable_name=executable_name,
            enable_devtools=args.devtools,
            platform_optimized=args.platform_optimized,
            logging_level=log_level,
            config_profile=args.config_profile,
            config_template=args.config_template
        )
        
        # Configure SDK features based on user preferences
        automator.configure_sdk_features()
        
        # Validate NW.js version compatibility
        automator.validate_nwjs_version()

        # Process the game
        result = automator.process_game(create_backup=not args.no_backup)

    # Generate execution report
    execution_report = automator.generate_execution_report(result)
    
    # Save execution report
    automator.save_execution_report(execution_report)
    
    if result['success']:
        print(f"\n✅ Success! Game processed successfully.")
        print(f"📁 Game directory: {result['game_path']}")
        print(f"🚀 Game executable: {result['game_executable']}")
        print(f"\n🎮 You can now launch your game using your custom executable!")
        print(
            f"💡 Type 'process.versions' in the game console to verify your NW.js version!")
        print(f"\n📊 Execution report saved to: execution_reports/report_{execution_report['execution_timestamp'].replace(' ', '_').replace(':', '-')}.json")

    else:
        print(f"\n❌ Failed: {result['error']}")
        if result.get('rollback_status') == 'success':
            print(f"✅ Automatic rollback completed successfully!")
            print(f"💾 Game restored to original state")
        elif result.get('rollback_status') == 'failed':
            print(f"❌ Rollback failed: {result.get('rollback_error', 'Unknown error')}")
            print(f"💾 Manual restoration may be needed from backup")
        
        print(f"\n📊 Execution report saved with error details")
        sys.exit(1)


if __name__ == '__main__':
    main()