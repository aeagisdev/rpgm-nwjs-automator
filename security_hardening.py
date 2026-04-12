#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NW.js Automator Security Hardening
Enhances security of the NW.js Automator tool
"""

import os
import sys
import json
import hashlib
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class SecurityHardener:
    """Enhances security of NW.js Automator operations"""
    
    def __init__(self):
        self.safe_file_patterns = [
            r'^[a-zA-Z0-9_\-\.]+$',  # Basic filename pattern
            r'^package\.json$',
            r'^index\.html$',
            r'^www/',
            r'^\.nwjs$',
            r'^nw(\.exe)?$',
            r'^nwjs(\.exe)?$'
        ]
        
        self.dangerous_extensions = [
            '.exe', '.dll', '.so', '.dylib', '.bat', '.cmd', '.ps1', '.sh',
            '.vbs', '.js', '.py', '.php', '.rb', '.pl', '.jar'
        ]
        
        self.safe_url_patterns = [
            r'^https://dl\.nwjs\.io/',
            r'^https://github\.com/',
            r'^https://api\.github\.com/',
            r'^https://raw\.githubusercontent\.com/'
        ]
    
    def validate_input_path(self, path: str) -> Tuple[bool, Optional[str]]:
        """Validate file/directory paths for security"""
        try:
            # Convert to Path object for safe handling
            path_obj = Path(path)
            
            # Check for path traversal attempts
            if '..' in str(path_obj) or path_obj.is_absolute() and any(
                part in ['\\', '/'] for part in str(path_obj).split(os.path.sep)
            ):
                return False, "Potential path traversal detected"
            
            # Check for null bytes
            if '\x00' in str(path_obj):
                return False, "Null bytes detected in path"
            
            # Check for control characters
            if any(ord(char) < 32 for char in str(path_obj)):
                return False, "Control characters detected in path"
            
            # Check path length
            if len(str(path_obj)) > 1024:
                return False, "Path too long"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"Path validation error: {e}")
            return False, f"Invalid path: {e}"
    
    def validate_filename(self, filename: str) -> Tuple[bool, Optional[str]]:
        """Validate filenames for security"""
        try:
            # Check for null bytes
            if '\x00' in filename:
                return False, "Null bytes detected in filename"
            
            # Check for control characters
            if any(ord(char) < 32 for char in filename):
                return False, "Control characters detected in filename"
            
            # Check for dangerous extensions
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in self.dangerous_extensions:
                return False, f"Dangerous file extension: {file_ext}"
            
            # Check filename length
            if len(filename) > 255:
                return False, "Filename too long"
            
            # Check against safe patterns
            safe = False
            for pattern in self.safe_file_patterns:
                if re.match(pattern, filename):
                    safe = True
                    break
            
            if not safe:
                return False, "Filename doesn't match safe patterns"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"Filename validation error: {e}")
            return False, f"Invalid filename: {e}"
    
    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """Validate URLs for security"""
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                return False, f"Unsupported URL scheme: {parsed.scheme}"
            
            # Check for dangerous schemes
            if parsed.scheme == 'http' and parsed.hostname not in ['localhost', '127.0.0.1']:
                return False, "HTTP URLs to external hosts are not allowed"
            
            # Check hostname
            if not parsed.hostname:
                return False, "Missing hostname"
            
            # Check for IP addresses (allow localhost)
            if parsed.hostname not in ['localhost', '127.0.0.1']:
                if re.match(r'^\d+\.\d+\.\d+\.\d+$', parsed.hostname):
                    return False, "Direct IP addresses not allowed"
            
            # Check against safe URL patterns
            safe = False
            for pattern in self.safe_url_patterns:
                if re.match(pattern, url):
                    safe = True
                    break
            
            if not safe:
                return False, "URL doesn't match safe patterns"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"URL validation error: {e}")
            return False, f"Invalid URL: {e}"
    
    def sanitize_package_json(self, package_data: Dict) -> Dict:
        """Sanitize package.json content for security"""
        sanitized = {}
        
        # Whitelist of allowed fields
        allowed_fields = {
            'name': str,
            'main': str,
            'window': dict,
            'chromium-args': str,
            'js-flags': str,
            'node-remote': bool,
            'webview_tag': bool,
            'single-instance': bool,
            'inject_js_start': str,
            'inject_js_end': str
        }
        
        for key, value in package_data.items():
            if key in allowed_fields:
                expected_type = allowed_fields[key]
                
                # Type checking
                if not isinstance(value, expected_type):
                    logger.warning(f"Invalid type for {key}: expected {expected_type}, got {type(value)}")
                    continue
                
                # Additional validation for specific fields
                if key == 'name':
                    # Validate name field
                    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', value):
                        logger.warning(f"Invalid package name: {value}")
                        continue
                
                elif key == 'main':
                    # Validate main field
                    if not value.startswith('www/') and not value.startswith('index.html'):
                        logger.warning(f"Invalid main path: {value}")
                        continue
                
                elif key == 'chromium-args':
                    # Validate chromium args
                    if any(dangerous in value for dangerous in ['--disable-web-security', '--allow-file-access-from-files']):
                        logger.warning(f"Dangerous chromium args detected: {value}")
                        continue
                
                sanitized[key] = value
            else:
                logger.warning(f"Disallowed field in package.json: {key}")
        
        # Ensure required fields are present
        if 'name' not in sanitized:
            sanitized['name'] = 'RPGGame'
        
        if 'main' not in sanitized:
            sanitized['main'] = 'www/index.html'
        
        return sanitized
    
    def check_file_permissions(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Check file permissions for security"""
        try:
            if not file_path.exists():
                return False, "File does not exist"
            
            # Get file stats
            stat_info = file_path.stat()
            
            # Check for world-writable files (security risk)
            if stat_info.st_mode & 0o002:
                return False, "File is world-writable"
            
            # Check for setuid/setgid bits (security risk)
            if stat_info.st_mode & (0o4000 | 0o2000):
                return False, "File has setuid or setgid bits set"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"File permission check error: {e}")
            return False, f"Could not check permissions: {e}"
    
    def calculate_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> Optional[str]:
        """Calculate file hash for integrity verification"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.warning(f"Could not calculate file hash: {e}")
            return None
    
    def verify_file_integrity(self, file_path: Path, expected_hash: str, 
                             algorithm: str = 'sha256') -> Tuple[bool, Optional[str]]:
        """Verify file integrity using hash comparison"""
        try:
            actual_hash = self.calculate_file_hash(file_path, algorithm)
            
            if not actual_hash:
                return False, "Could not calculate file hash"
            
            if actual_hash.lower() != expected_hash.lower():
                return False, f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"File integrity verification error: {e}")
            return False, f"Verification failed: {e}"
    
    def scan_for_suspicious_content(self, file_path: Path) -> List[str]:
        """Scan file content for suspicious patterns"""
        suspicious_patterns = [
            r'eval\(',
            r'document\.write\(',
            r'window\.location\.href\s*=\s*',
            r'\.innerHTML\s*=\s*',
            r'\.outerHTML\s*=\s*',
            r'\.appendChild\(',
            r'\.insertBefore\(',
            r'\.documentElement\.write\(',
            r'\.createElement\(',
            r'\.setAttribute\(',
            r'javascript:\s*',
            r'onerror\s*=\s*',
            r'onload\s*=\s*',
            r'onmouseover\s*=\s*',
            r'\<script\>',
            r'\<iframe\>',
            r'\<object\>',
            r'\<embed\>',
            r'\<applet\>',
            r'\<meta\s+http-equiv="refresh"',
            r'\.exec\(',
            r'\.execute\(',
            r'\.run\(',
            r'\.spawn\(',
            r'\.eval\(',
            r'require\(',
            r'import\(',
            r'__import__\(',
            r'exec\(',
            r'compile\('
        ]
        
        found_issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            for i, pattern in enumerate(suspicious_patterns):
                if re.search(pattern, content, re.IGNORECASE):
                    found_issues.append(f"Suspicious pattern {i+1}: {pattern}")
            
        except Exception as e:
            logger.warning(f"Could not scan file content: {e}")
            found_issues.append(f"Scan error: {e}")
        
        return found_issues
    
    def validate_json_structure(self, json_data: Dict, schema: Dict) -> Tuple[bool, List[str]]:
        """Validate JSON structure against a schema"""
        issues = []
        
        # Check required fields
        for required_field in schema.get('required', []):
            if required_field not in json_data:
                issues.append(f"Missing required field: {required_field}")
        
        # Check field types
        for field_name, field_schema in schema.get('properties', {}).items():
            if field_name in json_data:
                expected_type = field_schema.get('type')
                actual_value = json_data[field_name]
                
                if expected_type == 'string' and not isinstance(actual_value, str):
                    issues.append(f"Field {field_name} should be string, got {type(actual_value)}")
                
                elif expected_type == 'number' and not isinstance(actual_value, (int, float)):
                    issues.append(f"Field {field_name} should be number, got {type(actual_value)}")
                
                elif expected_type == 'boolean' and not isinstance(actual_value, bool):
                    issues.append(f"Field {field_name} should be boolean, got {type(actual_value)}")
                
                elif expected_type == 'object' and not isinstance(actual_value, dict):
                    issues.append(f"Field {field_name} should be object, got {type(actual_value)}")
                
                elif expected_type == 'array' and not isinstance(actual_value, list):
                    issues.append(f"Field {field_name} should be array, got {type(actual_value)}")
        
        return len(issues) == 0, issues
    
    def create_sandbox_environment(self, base_dir: Path) -> Path:
        """Create a sandboxed environment for safe operations"""
        try:
            # Create a temporary directory with restricted permissions
            sandbox_dir = base_dir / f"sandbox_{hashlib.md5(str(datetime.now()).encode()).hexdigest()}"
            sandbox_dir.mkdir(mode=0o700, exist_ok=True)
            
            # Create a restricted environment
            env_file = sandbox_dir / '.sandbox_env'
            env_data = {
                'created_at': datetime.now().isoformat(),
                'permissions': 'restricted',
                'allowed_operations': ['read', 'write', 'execute'],
                'network_access': False,
                'max_file_size': 1024 * 1024 * 100  # 100MB
            }
            
            with open(env_file, 'w', encoding='utf-8') as f:
                json.dump(env_data, f, indent=2)
            
            logger.info(f"✓ Sandbox environment created: {sandbox_dir}")
            return sandbox_dir
            
        except Exception as e:
            logger.error(f"Could not create sandbox environment: {e}")
            raise
    
    def validate_executable_safety(self, executable_path: Path) -> Tuple[bool, List[str]]:
        """Validate executable files for safety"""
        issues = []
        
        if not executable_path.exists():
            issues.append("Executable does not exist")
            return False, issues
        
        # Check file permissions
        valid, msg = self.check_file_permissions(executable_path)
        if not valid:
            issues.append(f"Permission issue: {msg}")
        
        # Check for suspicious content in executable (basic check)
        try:
            with open(executable_path, 'rb') as f:
                # Read first 1KB for basic checks
                header = f.read(1024)
                
                # Check for common executable magic numbers
                if not (header.startswith(b'MZ') or  # Windows PE
                        header.startswith(b'\x7fELF') or  # Linux ELF
                        header.startswith(b'\xcf\xfa\xed\xfe')):  # Mach-O
                    issues.append("Invalid executable format")
        
        except Exception as e:
            issues.append(f"Could not validate executable: {e}")
        
        return len(issues) == 0, issues
    
    def get_security_recommendations(self) -> List[str]:
        """Get security best practice recommendations"""
        recommendations = [
            "🔒 Always validate user input before processing",
            "🔒 Use HTTPS for all network communications",
            "🔒 Regularly update dependencies to latest secure versions",
            "🔒 Implement proper error handling to avoid information leakage",
            "🔒 Use principle of least privilege for file permissions",
            "🔒 Validate file types and extensions before processing",
            "🔒 Implement rate limiting for network operations",
            "🔒 Use secure coding practices to prevent injection attacks",
            "🔒 Regularly audit code for security vulnerabilities",
            "🔒 Keep backup copies of critical files before modifications"
        ]
        
        return recommendations
    
    def validate_configuration(self, config: Dict) -> Tuple[bool, List[str]]:
        """Validate tool configuration for security"""
        issues = []
        
        # Check for dangerous settings
        if config.get('enable_devtools', False) and not config.get('development_mode', False):
            issues.append("Developer tools enabled in non-development mode")
        
        if config.get('allow_unsigned_executables', False):
            issues.append("Unsigned executables allowed")
        
        if config.get('disable_backups', False):
            issues.append("Backups disabled - data loss risk")
        
        if config.get('skip_validation', False):
            issues.append("Input validation skipped")
        
        # Check NW.js version safety
        nwjs_version = config.get('nwjs_version', 'v0.49.2')
        dangerous_versions = ['v0.13.0', 'v0.14.0', 'v0.15.0']  # Known vulnerable versions
        
        if any(ver in nwjs_version for ver in dangerous_versions):
            issues.append(f"Potentially vulnerable NW.js version: {nwjs_version}")
        
        return len(issues) == 0, issues
    
    def create_security_audit_report(self, audit_data: Dict) -> Dict:
        """Create a comprehensive security audit report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'security_audit': True,
            'findings': [],
            'recommendations': [],
            'severity': 'low'
        }
        
        # Analyze findings and determine severity
        high_severity_issues = [
            'path traversal', 'dangerous extension', 'world-writable',
            'setuid', 'hash mismatch', 'invalid executable'
        ]
        
        medium_severity_issues = [
            'permission issue', 'suspicious pattern', 'missing field',
            'invalid type', 'vulnerable version'
        ]
        
        for finding in audit_data.get('findings', []):
            report['findings'].append(finding)
            
            # Determine severity
            if any(issue in finding.lower() for issue in high_severity_issues):
                report['severity'] = 'high'
            elif any(issue in finding.lower() for issue in medium_severity_issues):
                if report['severity'] != 'high':
                    report['severity'] = 'medium'
        
        # Add recommendations based on severity
        if report['severity'] == 'high':
            report['recommendations'].extend([
                "🚨 CRITICAL: Immediate action required",
                "🔒 Review all security settings and configurations",
                "🔒 Update to latest secure versions",
                "🔒 Implement additional validation checks",
                "🔒 Consider rolling back recent changes"
            ])
        elif report['severity'] == 'medium':
            report['recommendations'].extend([
                "⚠️  WARNING: Security issues detected",
                "🔒 Review configuration and settings",
                "🔒 Update vulnerable components",
                "🔒 Implement additional security measures"
            ])
        else:
            report['recommendations'].extend([
                "✅ Security audit passed",
                "🔒 Continue following security best practices",
                "🔒 Regularly review and update security measures"
            ])
        
        return report


def validate_game_directory_security(game_dir: Path) -> Dict:
    """Validate game directory for security issues"""
    hardener = SecurityHardener()
    audit_results = {
        'findings': [],
        'warnings': [],
        'errors': []
    }
    
    # Validate directory path
    valid, msg = hardener.validate_input_path(str(game_dir))
    if not valid:
        audit_results['errors'].append(f"Directory path validation failed: {msg}")
        return audit_results
    
    # Check directory exists and is accessible
    if not game_dir.exists():
        audit_results['errors'].append("Game directory does not exist")
        return audit_results
    
    if not game_dir.is_dir():
        audit_results['errors'].append("Game path is not a directory")
        return audit_results
    
    # Check critical files
    critical_files = ['package.json', 'www', 'index.html']
    
    for critical_file in critical_files:
        file_path = game_dir / critical_file
        
        if not file_path.exists():
            audit_results['warnings'].append(f"Missing critical file: {critical_file}")
            continue
        
        # Validate file permissions
        valid, msg = hardener.check_file_permissions(file_path)
        if not valid:
            audit_results['findings'].append(f"Permission issue with {critical_file}: {msg}")
        
        # Scan for suspicious content (for text files)
        if file_path.suffix in ['.json', '.html', '.js']:
            suspicious_content = hardener.scan_for_suspicious_content(file_path)
            if suspicious_content:
                audit_results['findings'].extend([
                    f"Suspicious content found in {critical_file}: {issue}"
                    for issue in suspicious_content
                ])
    
    # Validate package.json specifically
    package_json = game_dir / 'package.json'
    if package_json.exists():
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            sanitized_data = hardener.sanitize_package_json(package_data)
            
            if len(sanitized_data) != len(package_data):
                audit_results['findings'].append(
                    f"package.json contained {len(package_data) - len(sanitized_data)} disallowed fields"
                )
            
        except Exception as e:
            audit_results['errors'].append(f"Could not validate package.json: {e}")
    
    return audit_results


def create_security_profile() -> Dict:
    """Create a security profile with recommended settings"""
    return {
        'security_profile': 'recommended',
        'settings': {
            'enable_input_validation': True,
            'enable_file_permission_checks': True,
            'enable_network_validation': True,
            'enable_executable_validation': True,
            'enable_content_scanning': True,
            'allow_devtools_in_production': False,
            'allow_unsigned_executables': False,
            'allow_http_urls': False,
            'max_file_size_mb': 100,
            'backup_before_operations': True,
            'validate_checksums': True,
            'scan_for_malware': False,
            'use_sandbox': True
        },
        'recommendations': SecurityHardener().get_security_recommendations()
    }


if __name__ == "__main__":
    # Example usage
    hardener = SecurityHardener()
    
    print("🔒 NW.js Automator Security Hardening")
    print("=" * 50)
    
    # Test path validation
    test_paths = [
        "valid_game",
        "../dangerous_path",
        "/absolute/path",
        "path\x00with_null",
        "a" * 1025  # Too long
    ]
    
    print("📁 Path Validation Tests:")
    for path in test_paths:
        valid, msg = hardener.validate_input_path(path)
        status = "✅" if valid else "❌"
        print(f"   {status} {path}: {msg or 'OK'}")
    
    # Test filename validation
    test_filenames = [
        "valid_file.txt",
        "dangerous.exe",
        "script.js",
        "file\x00with_null.txt",
        "a" * 256 + ".txt"  # Too long
    ]
    
    print("\n📄 Filename Validation Tests:")
    for filename in test_filenames:
        valid, msg = hardener.validate_filename(filename)
        status = "✅" if valid else "❌"
        print(f"   {status} {filename}: {msg or 'OK'}")
    
    # Show security recommendations
    print("\n💡 Security Recommendations:")
    recommendations = hardener.get_security_recommendations()
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. {rec}")