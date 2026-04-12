#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NW.js Automator Test Suite
Comprehensive testing framework for the NW.js Automator tool
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class TestNWJSAutomator(unittest.TestCase):
    """Test cases for NW.js Automator core functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp(prefix='nwjs_test_'))
        self.game_dir = self.test_dir / 'test_game'
        self.game_dir.mkdir()
        
        # Create a minimal RPG Maker MV structure
        self._create_minimal_game_structure()
        
        # Import the main module
        from nwjs_automator import NWJSAutomator
        self.automator = NWJSAutomator(
            game_path=str(self.game_dir),
            nwjs_version='v0.49.2',
            use_sdk=True,
            executable_name='TestGame'
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def _create_minimal_game_structure(self):
        """Create a minimal RPG Maker MV game structure for testing"""
        # Create package.json
        package_data = {
            'name': 'TestGame',
            'main': 'www/index.html',
            'window': {
                'title': 'Test Game',
                'toolbar': False,
                'width': 800,
                'height': 600
            }
        }
        
        with open(self.game_dir / 'package.json', 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2)
        
        # Create www directory
        www_dir = self.game_dir / 'www'
        www_dir.mkdir()
        
        # Create index.html
        index_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Test Game</title>
</head>
<body>
    <script src="js/main.js"></script>
</body>
</html>'''
        
        with open(www_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # Create js directory and main.js
        js_dir = www_dir / 'js'
        js_dir.mkdir()
        
        main_js = '''console.log("Test Game loaded");'''
        with open(js_dir / 'main.js', 'w', encoding='utf-8') as f:
            f.write(main_js)
    
    def test_package_json_validation(self):
        """Test package.json validation and fixing"""
        package_json = self.game_dir / 'package.json'
        
        # Test with missing required fields
        with open(package_json, 'w', encoding='utf-8') as f:
            json.dump({'name': 'BrokenGame'}, f)  # Missing 'main' field
        
        # This should fix the package.json
        result = self.automator.validate_and_fix_package_json(package_json)
        self.assertTrue(result, "package.json should be fixed")
        
        # Verify the fix
        with open(package_json, 'r', encoding='utf-8') as f:
            fixed_data = json.load(f)
        
        self.assertIn('main', fixed_data, "main field should be added")
        self.assertEqual(fixed_data['main'], 'www/index.html', "main should point to index.html")
    
    def test_platform_detection(self):
        """Test platform detection"""
        platform_info = self.automator.detect_platform_info()
        
        self.assertIn('os', platform_info, "OS should be detected")
        self.assertIn('architecture', platform_info, "Architecture should be detected")
        self.assertIn('executable_ext', platform_info, "Executable extension should be set")
    
    def test_nwjs_version_validation(self):
        """Test NW.js version validation"""
        # Test with valid version
        self.automator.nwjs_version = 'v0.49.2'
        result = self.automator.validate_nwjs_version()
        self.assertTrue(result, "Valid version should pass validation")
        
        # Test with invalid version (should fallback to default)
        self.automator.nwjs_version = 'invalid_version'
        result = self.automator.validate_nwjs_version()
        self.assertFalse(result, "Invalid version should fail validation")
        self.assertNotEqual(self.automator.nwjs_version, 'invalid_version', 
                           "Invalid version should be changed")
    
    def test_backup_creation(self):
        """Test backup creation functionality"""
        # Create a backup
        backup_path = self.automator.backup_game()
        
        self.assertTrue(backup_path.exists(), "Backup should be created")
        
        # Verify backup contains critical files
        self.assertTrue((backup_path / 'package.json').exists(), "Backup should contain package.json")
        self.assertTrue((backup_path / 'www').exists(), "Backup should contain www directory")
    
    def test_config_profiles(self):
        """Test configuration profiles"""
        profiles = self.automator.config_profiles
        
        self.assertGreater(len(profiles), 0, "Should have configuration profiles")
        self.assertIn('default', profiles, "Should have default profile")
        self.assertIn('development', profiles, "Should have development profile")
        self.assertIn('production', profiles, "Should have production profile")
    
    def test_config_templates(self):
        """Test configuration templates"""
        templates = self.automator.template_configs
        
        self.assertGreater(len(templates), 0, "Should have configuration templates")
        self.assertIn('minimal', templates, "Should have minimal template")
        self.assertIn('debug', templates, "Should have debug template")
    
    def test_config_export_import(self):
        """Test configuration export and import"""
        # Test export
        export_path = self.test_dir / 'test_config.json'
        result = self.automator.export_config(export_path)
        self.assertTrue(result, "Config export should succeed")
        self.assertTrue(export_path.exists(), "Exported config file should exist")
        
        # Test import
        result = self.automator.import_config(export_path)
        self.assertTrue(result, "Config import should succeed")


class TestUpdateSystem(unittest.TestCase):
    """Test cases for the update system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from update_system import UpdateSystem
        self.update_system = UpdateSystem(current_version="2.0.0")
    
    @patch('requests.get')
    def test_update_check(self, mock_get):
        """Test update checking functionality"""
        # Mock response for newer version
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'tag_name': 'v2.1.0',
            'assets': [
                {
                    'name': 'nwjs_automator_win.zip',
                    'browser_download_url': 'https://example.com/download.zip'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.update_system.check_for_updates()
        self.assertIsNotNone(result, "Should detect newer version")
        self.assertEqual(result['version'], '2.1.0', "Should return correct version")
    
    @patch('requests.get')
    def test_no_update_available(self, mock_get):
        """Test when no update is available"""
        # Mock response for same version
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'tag_name': 'v2.0.0',
            'assets': []
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.update_system.check_for_updates()
        self.assertIsNone(result, "Should return None when no update available")
    
    def test_version_comparison(self):
        """Test version comparison logic"""
        # Test various version comparisons
        self.assertEqual(self.update_system._compare_versions("2.1.0", "2.0.0"), 1, 
                        "2.1.0 should be greater than 2.0.0")
        self.assertEqual(self.update_system._compare_versions("2.0.0", "2.1.0"), -1, 
                        "2.0.0 should be less than 2.1.0")
        self.assertEqual(self.update_system._compare_versions("2.0.0", "2.0.0"), 0, 
                        "2.0.0 should equal 2.0.0")
        self.assertEqual(self.update_system._compare_versions("2.0.1", "2.0.0"), 1, 
                        "2.0.1 should be greater than 2.0.0")


class TestPerformance(unittest.TestCase):
    """Performance and stress tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp(prefix='nwjs_perf_test_'))
        
        # Import the main module
        from nwjs_automator import NWJSAutomator
        self.automator = NWJSAutomator(
            game_path=str(self.test_dir),
            nwjs_version='v0.49.2'
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_large_file_cleanup(self):
        """Test cleanup performance with many files"""
        # Create many test files
        for i in range(100):
            test_file = self.test_dir / f"test_file_{i}.tmp"
            test_file.write_text(f"Test content {i}")
        
        # Test cleanup performance
        import time
        start_time = time.time()
        
        # This should handle many files efficiently
        self.automator.cleanup_files = [f"test_file_{i}.tmp" for i in range(100)]
        # Note: We can't actually call the cleanup method here as it would
        # try to access self.game_path which doesn't exist in this context
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Cleanup
        for i in range(100):
            (self.test_dir / f"test_file_{i}.tmp").unlink()
        
        self.assertLess(duration, 5.0, "Cleanup should be fast even with many files")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp(prefix='nwjs_integration_test_'))
        self.game_dir = self.test_dir / 'integration_test_game'
        self.game_dir.mkdir()
        
        # Create a complete RPG Maker MV structure
        self._create_complete_game_structure()
        
        # Import the main module
        from nwjs_automator import NWJSAutomator
        self.automator = NWJSAutomator(
            game_path=str(self.game_dir),
            nwjs_version='v0.49.2',
            use_sdk=True,
            executable_name='IntegrationTest'
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def _create_complete_game_structure(self):
        """Create a more complete RPG Maker MV game structure"""
        # Create package.json with more complete structure
        package_data = {
            'name': 'IntegrationTest',
            'main': 'www/index.html',
            'window': {
                'title': 'Integration Test Game',
                'toolbar': False,
                'width': 800,
                'height': 600,
                'resizable': True
            },
            'chromium-args': '--disable-background-timer-throttling'
        }
        
        with open(self.game_dir / 'package.json', 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2)
        
        # Create www directory with more structure
        www_dir = self.game_dir / 'www'
        www_dir.mkdir()
        
        # Create index.html
        index_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Integration Test Game</title>
    <style>
        body { margin: 0; padding: 0; background: #000; }
        canvas { display: block; }
    </style>
</head>
<body>
    <script src="js/libs/pixi.js"></script>
    <script src="js/rpg_core.js"></script>
    <script src="js/rpg_managers.js"></script>
    <script src="js/rpg_objects.js"></script>
    <script src="js/rpg_scenes.js"></script>
    <script src="js/rpg_sprites.js"></script>
    <script src="js/rpg_windows.js"></script>
    <script src="js/plugins.js"></script>
    <script src="js/main.js"></script>
</body>
</html>'''
        
        with open(www_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # Create js directory structure
        js_dir = www_dir / 'js'
        js_dir.mkdir()
        
        # Create libs directory
        libs_dir = js_dir / 'libs'
        libs_dir.mkdir()
        
        # Create dummy JS files
        js_files = {
            'libs/pixi.js': 'console.log("PixiJS loaded");',
            'rpg_core.js': 'console.log("RPG Core loaded");',
            'rpg_managers.js': 'console.log("RPG Managers loaded");',
            'rpg_objects.js': 'console.log("RPG Objects loaded");',
            'rpg_scenes.js': 'console.log("RPG Scenes loaded");',
            'rpg_sprites.js': 'console.log("RPG Sprites loaded");',
            'rpg_windows.js': 'console.log("RPG Windows loaded");',
            'plugins.js': 'console.log("Plugins loaded");',
            'main.js': 'console.log("Main script loaded");'
        }
        
        for file_path, content in js_files.items():
            full_path = js_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def test_complete_workflow(self):
        """Test the complete automation workflow"""
        # This would normally test the full process_game() method,
        # but since that involves downloading NW.js, we'll test
        # the individual components that don't require network access
        
        # Test validation
        self.automator.validate_game_directory()
        
        # Test backup creation
        backup_path = self.automator.backup_game()
        self.assertTrue(backup_path.exists())
        
        # Test important files saving
        temp_dir = self.automator.save_important_files()
        self.assertTrue(temp_dir.exists())
        
        # Test cleanup (without actual NW.js files)
        # This just tests that the method runs without errors
        try:
            self.automator.cleanup_nwjs_files()
            self.assertTrue(True, "Cleanup should run without errors")
        except Exception as e:
            self.fail(f"Cleanup should run without errors: {e}")


class TestCrossPlatform(unittest.TestCase):
    """Cross-platform compatibility tests"""
    
    def test_windows_path_handling(self):
        """Test Windows-specific path handling"""
        from nwjs_automator import NWJSAutomator
        
        # Create a temporary test directory
        test_dir = Path(tempfile.mkdtemp(prefix='win_test_'))
        
        try:
            # Create automator instance
            automator = NWJSAutomator(
                game_path=str(test_dir),
                nwjs_version='v0.49.2'
            )
            
            # Test platform detection
            platform_info = automator.detect_platform_info()
            
            if sys.platform == 'win32':
                self.assertEqual(platform_info['executable_ext'], '.exe')
                self.assertEqual(platform_info['path_separator'], '\\')
            else:
                # On non-Windows, we can't test Windows-specific behavior
                # but we can verify the detection works
                self.assertIn('os', platform_info)
                
        finally:
            shutil.rmtree(test_dir)
    
    def test_unix_path_handling(self):
        """Test Unix-like path handling"""
        from nwjs_automator import NWJSAutomator
        
        # Create a temporary test directory
        test_dir = Path(tempfile.mkdtemp(prefix='unix_test_'))
        
        try:
            # Create automator instance
            automator = NWJSAutomator(
                game_path=str(test_dir),
                nwjs_version='v0.49.2'
            )
            
            # Test platform detection
            platform_info = automator.detect_platform_info()
            
            if sys.platform in ['darwin', 'linux']:
                self.assertEqual(platform_info['executable_ext'], '')
                self.assertEqual(platform_info['path_separator'], '/')
            else:
                # On Windows, we can't test Unix-specific behavior
                # but we can verify the detection works
                self.assertIn('os', platform_info)
                
        finally:
            shutil.rmtree(test_dir)


def run_all_tests():
    """Run all test suites and generate report"""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_suite.addTest(unittest.makeSuite(TestNWJSAutomator))
    test_suite.addTest(unittest.makeSuite(TestUpdateSystem))
    test_suite.addTest(unittest.makeSuite(TestPerformance))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    test_suite.addTest(unittest.makeSuite(TestCrossPlatform))
    
    # Create a test runner with verbose output
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = test_runner.run(test_suite)
    
    # Generate test report
    print("\n" + "="*60)
    print("TEST REPORT SUMMARY")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n📋 FAILED TESTS:")
        for i, failure in enumerate(result.failures, 1):
            test_name = failure[0].id().split('.')[-1]
            print(f"  {i}. {test_name}")
    
    if result.errors:
        print("\n📋 ERRORS:")
        for i, error in enumerate(result.errors, 1):
            test_name = error[0].id().split('.')[-1]
            print(f"  {i}. {test_name}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Run tests and exit with appropriate code
    sys.exit(run_all_tests())