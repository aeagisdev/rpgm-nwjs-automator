#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Batch Processing Module for NW.js Automator
Handles processing multiple RPG Maker MV games simultaneously
"""

import os
import json
import logging
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from nwjs_automator import NWJSAutomator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class BatchProcessor:
    """Handles batch processing of multiple RPG Maker MV games"""
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.worker_threads = []
        self.task_queue = queue.Queue()
        self.results = {}
        self.progress_callback = None
        self.message_callback = None
        self.completion_callback = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        # Statistics
        self.total_games = 0
        self.completed_games = 0
        self.failed_games = 0
        
    def add_game(self, game_path: str, config: dict):
        """Add a game to the batch processing queue"""
        if not Path(game_path).exists():
            raise FileNotFoundError(f"Game directory not found: {game_path}")
        
        with self.lock:
            self.total_games += 1
            self.task_queue.put((game_path, config))
        
        logger.info(f"Added game to batch queue: {game_path}")
    
    def set_callbacks(self, progress_callback=None, message_callback=None, completion_callback=None):
        """Set callback functions for progress updates"""
        self.progress_callback = progress_callback
        self.message_callback = message_callback
        self.completion_callback = completion_callback
    
    def _worker(self):
        """Worker thread function to process games"""
        while not self.stop_event.is_set():
            try:
                # Get next task
                game_path, config = self.task_queue.get(timeout=1)
                
                # Process the game
                self._process_single_game(game_path, config)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
                if self.message_callback:
                    self.message_callback(f"Worker error: {e}", "ERROR")
    
    def _process_single_game(self, game_path: str, config: dict):
        """Process a single game with error handling"""
        game_name = Path(game_path).name
        
        try:
            # Update progress
            if self.progress_callback:
                progress = (self.completed_games / self.total_games) * 100
                self.progress_callback(progress, f"Processing {game_name}...")
            
            if self.message_callback:
                self.message_callback(f"Starting processing for {game_name}", "INFO")
            
            # Create automator instance
            automator = NWJSAutomator(
                game_path=game_path,
                nwjs_version=config['nwjs_version'],
                use_sdk=config['use_sdk'],
                executable_name=config['executable_name'],
                enable_devtools=config['enable_devtools'],
                platform_optimized=config['platform_optimized'],
                logging_level=config['logging_level'],
                config_profile=config.get('config_profile'),
                config_template=config.get('config_template')
            )
            
            # Process the game
            result = automator.process_game(create_backup=config['create_backup'])
            
            with self.lock:
                self.completed_games += 1
                if result['success']:
                    self.results[game_path] = {
                        'success': True,
                        'game_executable': str(result['game_executable']),
                        'message': 'Processing completed successfully'
                    }
                else:
                    self.failed_games += 1
                    self.results[game_path] = {
                        'success': False,
                        'error': result.get('error', 'Unknown error'),
                        'rollback_status': result.get('rollback_status', 'not_attempted')
                    }
            
            # Update progress
            if self.progress_callback:
                progress = (self.completed_games / self.total_games) * 100
                status = f"Completed {self.completed_games}/{self.total_games} games"
                self.progress_callback(progress, status)
            
            if self.message_callback:
                if result['success']:
                    self.message_callback(f"✅ Successfully processed {game_name}", "SUCCESS")
                else:
                    self.message_callback(f"❌ Failed to process {game_name}", "ERROR")
                    
        except Exception as e:
            with self.lock:
                self.failed_games += 1
                self.completed_games += 1
                self.results[game_path] = {
                    'success': False,
                    'error': str(e),
                    'rollback_status': 'not_attempted'
                }
            
            if self.message_callback:
                self.message_callback(f"❌ Error processing {game_name}: {e}", "ERROR")
            
            if self.progress_callback:
                progress = (self.completed_games / self.total_games) * 100
                self.progress_callback(progress, f"Error processing {game_name}")
    
    def start_processing(self):
        """Start batch processing with worker threads"""
        if self.total_games == 0:
            raise ValueError("No games in the batch queue")
        
        logger.info(f"Starting batch processing with {self.max_workers} workers")
        
        # Create and start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, name=f"Worker-{i+1}")
            worker.start()
            self.worker_threads.append(worker)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_progress)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def _monitor_progress(self):
        """Monitor overall progress and notify when complete"""
        while not self.stop_event.is_set():
            if self.completed_games >= self.total_games:
                # All games processed
                self.stop_processing()
                
                # Generate summary
                summary = self._generate_summary()
                
                if self.message_callback:
                    self.message_callback("🎉 Batch processing completed!", "SUCCESS")
                    for line in summary:
                        self.message_callback(line, "INFO")
                
                if self.completion_callback:
                    self.completion_callback(self.results)
                
                break
            
            self.stop_event.wait(1)
    
    def stop_processing(self):
        """Stop all worker threads"""
        logger.info("Stopping batch processing...")
        self.stop_event.set()
        
        # Wait for all workers to finish
        for worker in self.worker_threads:
            worker.join(timeout=5)
            if worker.is_alive():
                logger.warning(f"Worker {worker.name} did not stop gracefully")
        
        self.worker_threads = []
        logger.info("Batch processing stopped")
    
    def _generate_summary(self) -> List[str]:
        """Generate a summary of batch processing results"""
        summary = []
        
        summary.append("=" * 60)
        summary.append("BATCH PROCESSING SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Total games processed: {self.total_games}")
        summary.append(f"Successfully completed: {self.completed_games}")
        summary.append(f"Failed: {self.failed_games}")
        summary.append(f"Success rate: {(self.completed_games / self.total_games) * 100:.1f}%")
        summary.append("-" * 60)
        
        # Add details for each game
        for game_path, result in self.results.items():
            game_name = Path(game_path).name
            if result['success']:
                summary.append(f"✅ {game_name}: SUCCESS")
                summary.append(f"   Executable: {result['game_executable']}")
            else:
                summary.append(f"❌ {game_name}: FAILED")
                summary.append(f"   Error: {result['error']}")
                if result.get('rollback_status') == 'success':
                    summary.append(f"   Rollback: SUCCESS")
                elif result.get('rollback_status') == 'failed':
                    summary.append(f"   Rollback: FAILED")
        
        summary.append("=" * 60)
        
        return summary
    
    def save_results(self, output_path: str = None):
        """Save batch processing results to a file"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"batch_results_{timestamp}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'total_games': self.total_games,
            'completed_games': self.completed_games,
            'failed_games': self.failed_games,
            'success_rate': (self.completed_games / self.total_games) * 100,
            'results': self.results
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Batch results saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save batch results: {e}")
            return False
    
    def load_config_from_file(self, config_file: str) -> dict:
        """Load batch configuration from a JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Loaded batch config from: {config_file}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load batch config: {e}")
            raise ValueError(f"Invalid configuration file: {e}")
    
    def save_config_to_file(self, config: dict, output_path: str = None) -> bool:
        """Save batch configuration to a JSON file"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"batch_config_{timestamp}.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Batch config saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save batch config: {e}")
            return False


class BatchConfigManager:
    """Manages batch processing configurations and presets"""
    
    def __init__(self):
        self.presets = {
            'default': {
                'name': 'Default Batch Configuration',
                'description': 'Balanced settings for most RPG Maker MV games',
                'settings': {
                    'nwjs_version': 'v0.49.2',
                    'use_sdk': False,
                    'enable_devtools': False,
                    'platform_optimized': True,
                    'create_backup': True,
                    'executable_name': 'Game',
                    'logging_level': 'INFO'
                }
            },
            'development': {
                'name': 'Development Batch Configuration',
                'description': 'Settings optimized for game development',
                'settings': {
                    'nwjs_version': 'v0.72.0',
                    'use_sdk': True,
                    'enable_devtools': True,
                    'platform_optimized': True,
                    'create_backup': True,
                    'executable_name': 'GameDev',
                    'logging_level': 'DEBUG'
                }
            },
            'production': {
                'name': 'Production Batch Configuration',
                'description': 'Settings optimized for final distribution',
                'settings': {
                    'nwjs_version': 'v0.49.2',
                    'use_sdk': False,
                    'enable_devtools': False,
                    'platform_optimized': True,
                    'create_backup': True,
                    'executable_name': 'Game',
                    'logging_level': 'INFO'
                }
            }
        }
    
    def get_preset_names(self) -> List[str]:
        """Get list of available preset names"""
        return list(self.presets.keys())
    
    def get_preset(self, preset_name: str) -> dict:
        """Get a specific preset configuration"""
        if preset_name not in self.presets:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        return self.presets[preset_name]
    
    def create_custom_config(self, config_data: dict) -> dict:
        """Create a custom batch configuration"""
        # Validate and merge with defaults
        default_config = self.presets['default']['settings'].copy()
        default_config.update(config_data)
        
        return {
            'name': config_data.get('name', 'Custom Configuration'),
            'description': config_data.get('description', 'Custom batch configuration'),
            'settings': default_config
        }
    
    def save_preset(self, preset_name: str, preset_data: dict) -> bool:
        """Save a custom preset"""
        try:
            self.presets[preset_name] = preset_data
            
            # Save to file
            presets_file = Path.home() / '.nwjs_automator_presets.json'
            with open(presets_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved preset: {preset_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save preset: {e}")
            return False
    
    def load_presets(self):
        """Load presets from file"""
        presets_file = Path.home() / '.nwjs_automator_presets.json'
        
        if presets_file.exists():
            try:
                with open(presets_file, 'r', encoding='utf-8') as f:
                    self.presets = json.load(f)
                logger.info(f"Loaded {len(self.presets)} presets")
            except Exception as e:
                logger.warning(f"Could not load presets: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    print("NW.js Automator Batch Processor")
    print("=" * 50)
    
    # Create batch processor
    processor = BatchProcessor(max_workers=2)
    
    # Set callbacks for progress updates
    def progress_callback(progress, message):
        print(f"Progress: {progress:.1f}% - {message}")
    
    def message_callback(message, level):
        print(f"[{level}] {message}")
    
    def completion_callback(results):
        print("\nBatch processing completed!")
        print(f"Success: {len([r for r in results.values() if r['success']])}")
        print(f"Failed: {len([r for r in results.values() if not r['success']])}")
    
    processor.set_callbacks(
        progress_callback=progress_callback,
        message_callback=message_callback,
        completion_callback=completion_callback
    )
    
    # Example: Add some games (this would be replaced with actual game paths)
    # processor.add_game("/path/to/game1", {
    #     'nwjs_version': 'v0.49.2',
    #     'use_sdk': False,
    #     'executable_name': 'Game1',
    #     'enable_devtools': False,
    #     'platform_optimized': True,
    #     'create_backup': True,
    #     'logging_level': 'INFO'
    # })
    
    print("\nNote: This is a demonstration. To use batch processing,")
    print("add actual game paths using the add_game() method.")
    print("\nExample:")
    print("processor.add_game('/path/to/your/game', config)")
    print("processor.start_processing()")