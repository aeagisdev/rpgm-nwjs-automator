#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin System for NW.js Automator
Framework for extending functionality through plugins
"""

import os
import json
import logging
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Optional, Type, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Base exception for plugin system errors"""
    pass


class PluginValidationError(PluginError):
    """Exception for plugin validation errors"""
    pass


class PluginInterface:
    """Base interface that all plugins must implement"""
    
    def __init__(self):
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.description = "Base plugin interface"
        self.requires = []  # List of required plugins
        self.compatible_with = []  # List of compatible NW.js Automator versions
    
    def initialize(self, automator_instance):
        """Initialize the plugin with the automator instance"""
        self.automator = automator_instance
        logger.info(f"Initialized plugin: {self.name}")
    
    def get_hooks(self) -> Dict[str, Any]:
        """Return dictionary of hook functions that this plugin provides"""
        return {}
    
    def validate_config(self, config: dict) -> bool:
        """Validate plugin configuration"""
        return True
    
    def cleanup(self):
        """Clean up resources when plugin is unloaded"""
        pass


class PluginManager:
    """Manages loading, validation, and execution of plugins"""
    
    def __init__(self):
        self.plugins = {}
        self.hook_registry = {}
        self.plugin_dirs = []
        self.loaded_plugins = []
        
        # Default plugin directories
        self._setup_default_plugin_dirs()
    
    def _setup_default_plugin_dirs(self):
        """Set up default plugin directories"""
        # Add current directory plugins folder
        current_dir = Path(__file__).parent
        plugins_dir = current_dir / "plugins"
        if plugins_dir.exists():
            self.add_plugin_directory(str(plugins_dir))
        
        # Add user home directory plugins
        home_plugins = Path.home() / ".nwjs_automator" / "plugins"
        if home_plugins.exists():
            self.add_plugin_directory(str(home_plugins))
    
    def add_plugin_directory(self, directory: str):
        """Add a directory to search for plugins"""
        directory = Path(directory)
        if directory.exists() and directory not in self.plugin_dirs:
            self.plugin_dirs.append(directory)
            logger.info(f"Added plugin directory: {directory}")
        elif not directory.exists():
            logger.warning(f"Plugin directory does not exist: {directory}")
    
    def discover_plugins(self) -> Dict[str, dict]:
        """Discover available plugins in all plugin directories"""
        discovered_plugins = {}
        
        for plugin_dir in self.plugin_dirs:
            for plugin_file in plugin_dir.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                
                try:
                    plugin_info = self._get_plugin_info_from_file(plugin_file)
                    if plugin_info:
                        plugin_name = plugin_info.get('name', plugin_file.stem)
                        discovered_plugins[plugin_name] = {
                            'file': str(plugin_file),
                            'directory': str(plugin_dir),
                            'info': plugin_info
                        }
                except Exception as e:
                    logger.warning(f"Could not load plugin {plugin_file}: {e}")
        
        logger.info(f"Discovered {len(discovered_plugins)} plugins")
        return discovered_plugins
    
    def _get_plugin_info_from_file(self, plugin_file: Path) -> Optional[dict]:
        """Extract plugin information from a Python file"""
        try:
            # Import the module dynamically
            module_name = f"plugin_{plugin_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, str(plugin_file))
            module = importlib.util.module_from_spec(spec)
            
            # Look for plugin classes in the module
            spec.loader.exec_module(module)
            
            # Find classes that inherit from PluginInterface
            plugin_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, PluginInterface) and obj != PluginInterface:
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                return None
            
            # Get info from the first plugin class found
            plugin_class = plugin_classes[0]
            plugin_instance = plugin_class()
            
            return {
                'name': getattr(plugin_instance, 'name', plugin_file.stem),
                'version': getattr(plugin_instance, 'version', '1.0.0'),
                'author': getattr(plugin_instance, 'author', 'Unknown'),
                'description': getattr(plugin_instance, 'description', 'No description'),
                'requires': getattr(plugin_instance, 'requires', []),
                'compatible_with': getattr(plugin_instance, 'compatible_with', []),
                'class_name': plugin_class.__name__
            }
            
        except Exception as e:
            logger.warning(f"Could not extract plugin info from {plugin_file}: {e}")
            return None
    
    def load_plugin(self, plugin_name: str, automator_instance=None) -> bool:
        """Load a plugin by name"""
        discovered = self.discover_plugins()
        
        if plugin_name not in discovered:
            raise PluginError(f"Plugin not found: {plugin_name}")
        
        plugin_info = discovered[plugin_name]
        plugin_file = Path(plugin_info['file'])
        
        try:
            # Import the plugin module
            module_name = f"plugin_{plugin_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, str(plugin_file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find and instantiate the plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, PluginInterface) and obj != PluginInterface:
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise PluginValidationError(f"No valid plugin class found in {plugin_file}")
            
            # Create plugin instance
            plugin_instance = plugin_class()
            
            # Validate plugin
            self._validate_plugin(plugin_instance)
            
            # Initialize plugin
            if automator_instance:
                plugin_instance.initialize(automator_instance)
            
            # Register plugin hooks
            hooks = plugin_instance.get_hooks()
            for hook_name, hook_func in hooks.items():
                if hook_name not in self.hook_registry:
                    self.hook_registry[hook_name] = []
                self.hook_registry[hook_name].append((plugin_name, hook_func))
            
            # Store loaded plugin
            self.plugins[plugin_name] = {
                'instance': plugin_instance,
                'file': str(plugin_file),
                'hooks': list(hooks.keys())
            }
            self.loaded_plugins.append(plugin_name)
            
            logger.info(f"✅ Successfully loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            raise PluginError(f"Failed to load plugin: {e}")
    
    def _validate_plugin(self, plugin_instance: PluginInterface):
        """Validate a plugin before loading"""
        # Check required attributes
        required_attrs = ['name', 'version', 'author', 'description']
        for attr in required_attrs:
            if not getattr(plugin_instance, attr, None):
                raise PluginValidationError(f"Plugin missing required attribute: {attr}")
        
        # Check compatibility
        # TODO: Add version compatibility checking
        
        # Check dependencies
        if plugin_instance.requires:
            missing_deps = [dep for dep in plugin_instance.requires if dep not in self.loaded_plugins]
            if missing_deps:
                raise PluginValidationError(f"Missing required plugins: {', '.join(missing_deps)}")
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin by name"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin_data = self.plugins[plugin_name]
            plugin_instance = plugin_data['instance']
            
            # Clean up plugin
            plugin_instance.cleanup()
            
            # Remove plugin hooks
            for hook_name in plugin_data['hooks']:
                if hook_name in self.hook_registry:
                    self.hook_registry[hook_name] = [
                        (name, func) for name, func in self.hook_registry[hook_name]
                        if name != plugin_name
                    ]
                    if not self.hook_registry[hook_name]:
                        del self.hook_registry[hook_name]
            
            # Remove from loaded plugins
            del self.plugins[plugin_name]
            if plugin_name in self.loaded_plugins:
                self.loaded_plugins.remove(plugin_name)
            
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def unload_all_plugins(self):
        """Unload all loaded plugins"""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
    
    def call_hooks(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Call all registered hooks for a specific hook name"""
        results = []
        
        if hook_name not in self.hook_registry:
            return results
        
        for plugin_name, hook_func in self.hook_registry[hook_name]:
            try:
                result = hook_func(*args, **kwargs)
                results.append((plugin_name, result))
                logger.debug(f"Called hook {hook_name} from plugin {plugin_name}")
            except Exception as e:
                logger.error(f"Error calling hook {hook_name} from plugin {plugin_name}: {e}")
                results.append((plugin_name, None))
        
        return results
    
    def get_loaded_plugins(self) -> List[dict]:
        """Get information about loaded plugins"""
        return [
            {
                'name': name,
                'version': data['instance'].version,
                'author': data['instance'].author,
                'description': data['instance'].description,
                'hooks': data['hooks'],
                'file': data['file']
            }
            for name, data in self.plugins.items()
        ]
    
    def get_available_hooks(self) -> List[str]:
        """Get list of available hooks"""
        return list(self.hook_registry.keys())
    
    def load_plugins_from_config(self, config: dict, automator_instance=None):
        """Load plugins from a configuration dictionary"""
        plugins_to_load = config.get('plugins', [])
        loaded_count = 0
        
        for plugin_config in plugins_to_load:
            plugin_name = plugin_config.get('name')
            if plugin_name:
                try:
                    self.load_plugin(plugin_name, automator_instance)
                    loaded_count += 1
                except Exception as e:
                    logger.warning(f"Could not load plugin {plugin_name}: {e}")
        
        logger.info(f"Loaded {loaded_count} plugins from configuration")
        return loaded_count
    
    def save_plugin_config(self, output_path: str = None) -> bool:
        """Save current plugin configuration to a file"""
        if not output_path:
            output_path = Path.home() / '.nwjs_automator_plugins.json'
        
        config = {
            'plugins': [
                {
                    'name': name,
                    'enabled': True,
                    'config': {}
                }
                for name in self.loaded_plugins
            ],
            'plugin_directories': [str(dir) for dir in self.plugin_dirs]
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Plugin configuration saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save plugin configuration: {e}")
            return False
    
    def load_plugin_config(self, config_path: str = None) -> dict:
        """Load plugin configuration from a file"""
        if not config_path:
            config_path = Path.home() / '.nwjs_automator_plugins.json'
        
        if not Path(config_path).exists():
            return {'plugins': [], 'plugin_directories': []}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Loaded plugin configuration from: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load plugin configuration: {e}")
            return {'plugins': [], 'plugin_directories': []}


# Example plugin implementations
class ExamplePlugin(PluginInterface):
    """Example plugin demonstrating the plugin interface"""
    
    def __init__(self):
        super().__init__()
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.author = "NW.js Automator Team"
        self.description = "Example plugin showing how to create plugins"
        self.requires = []
        self.compatible_with = ["2.0.0", "2.1.0"]
    
    def initialize(self, automator_instance):
        super().initialize(automator_instance)
        logger.info("Example plugin initialized with automator instance")
    
    def get_hooks(self) -> Dict[str, Any]:
        return {
            'pre_process_game': self.pre_process_game_hook,
            'post_process_game': self.post_process_game_hook,
            'validate_package_json': self.validate_package_json_hook
        }
    
    def pre_process_game_hook(self, game_path: str) -> dict:
        """Hook called before processing a game"""
        logger.info(f"Example plugin: Pre-processing game at {game_path}")
        return {'status': 'success', 'message': 'Pre-processing completed'}
    
    def post_process_game_hook(self, game_path: str, result: dict) -> dict:
        """Hook called after processing a game"""
        logger.info(f"Example plugin: Post-processing game at {game_path}")
        return {'status': 'success', 'message': 'Post-processing completed'}
    
    def validate_package_json_hook(self, package_json_data: dict) -> dict:
        """Hook for additional package.json validation"""
        # Example: Add custom validation rules
        if 'customField' in package_json_data:
            logger.info("Example plugin: Found custom field in package.json")
        
        return {'valid': True, 'warnings': []}


class FileOptimizationPlugin(PluginInterface):
    """Plugin for advanced file optimization"""
    
    def __init__(self):
        super().__init__()
        self.name = "File Optimization Plugin"
        self.version = "1.1.0"
        self.author = "NW.js Automator Team"
        self.description = "Provides advanced file optimization features"
        self.requires = []
        self.compatible_with = ["2.1.0"]
        self.optimization_level = "balanced"
    
    def initialize(self, automator_instance):
        super().initialize(automator_instance)
        # Could load configuration here
        pass
    
    def get_hooks(self) -> Dict[str, Any]:
        return {
            'pre_cleanup': self.pre_cleanup_hook,
            'file_optimization': self.file_optimization_hook
        }
    
    def pre_cleanup_hook(self, cleanup_files: list) -> dict:
        """Hook called before file cleanup"""
        # Add additional files to cleanup based on optimization level
        additional_files = []
        
        if self.optimization_level == "aggressive":
            additional_files = ['nw_100_percent.pak', 'nw_200_percent.pak']
        
        return {
            'additional_files': additional_files,
            'message': f'Added {len(additional_files)} files for aggressive cleanup'
        }
    
    def file_optimization_hook(self, game_path: str) -> dict:
        """Perform file optimization"""
        # This would contain actual optimization logic
        logger.info(f"Performing file optimization for {game_path}")
        return {'optimized_files': 0, 'saved_space': '0MB'}


# Plugin system testing and demonstration
if __name__ == "__main__":
    print("NW.js Automator Plugin System")
    print("=" * 50)
    
    # Create plugin manager
    plugin_manager = PluginManager()
    
    # Discover plugins
    print("\nDiscovering plugins...")
    discovered = plugin_manager.discover_plugins()
    
    if discovered:
        print(f"Found {len(discovered)} plugins:")
        for name, info in discovered.items():
            print(f"  - {name} v{info['info']['version']}: {info['info']['description']}")
    else:
        print("No plugins found in default directories.")
    
    # Example: Load built-in example plugin
    print("\nLoading example plugins...")
    
    # Create a temporary plugin file for demonstration
    temp_plugin_dir = Path("temp_plugins")
    temp_plugin_dir.mkdir(exist_ok=True)
    
    example_plugin_file = temp_plugin_dir / "example_plugin.py"
    with open(example_plugin_file, 'w', encoding='utf-8') as f:
        f.write('''
from plugin_system import PluginInterface
import logging

logger = logging.getLogger(__name__)

class DemoPlugin(PluginInterface):
    def __init__(self):
        super().__init__()
        self.name = "Demo Plugin"
        self.version = "1.0.0"
        self.author = "Demo Author"
        self.description = "A demonstration plugin"
        self.requires = []
        self.compatible_with = ["2.0.0"]
    
    def get_hooks(self):
        return {
            'pre_process_game': self.demo_hook
        }
    
    def demo_hook(self, game_path):
        logger.info(f"Demo plugin hook called for: {game_path}")
        return {'status': 'success', 'message': 'Demo hook executed'}
''')
    
    # Add the temp directory to plugin manager
    plugin_manager.add_plugin_directory(str(temp_plugin_dir))
    
    # Discover again
    discovered = plugin_manager.discover_plugins()
    if 'Demo Plugin' in discovered:
        try:
            plugin_manager.load_plugin('Demo Plugin')
            print("✅ Successfully loaded demo plugin")
            
            # Test calling hooks
            results = plugin_manager.call_hooks('pre_process_game', '/fake/game/path')
            print(f"Hook results: {results}")
            
        except Exception as e:
            print(f"❌ Failed to load demo plugin: {e}")
    
    # Clean up
    import shutil
    if temp_plugin_dir.exists():
        shutil.rmtree(temp_plugin_dir)
    
    print("\nPlugin system demonstration completed.")
    print("\nTo create your own plugins:")
    print("1. Create a Python file in a plugins directory")
    print("2. Inherit from PluginInterface")
    print("3. Implement the required methods")
    print("4. Define your hooks in get_hooks()")
    print("5. The plugin will be automatically discovered and loaded")