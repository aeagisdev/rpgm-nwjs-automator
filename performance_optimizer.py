#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NW.js Automator Performance Optimizer
Optimizes performance of the NW.js Automator tool
"""

import os
import sys
import json
import shutil
import tempfile
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import time
import functools
import concurrent.futures
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Optimizes performance of NW.js Automator operations"""
    
    def __init__(self):
        self.cache_dir = Path(tempfile.gettempdir()) / 'nwjs_automator_cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.max_workers = min(4, os.cpu_count() or 1)
        
    def enable_caching(self, func):
        """Decorator to enable caching for expensive operations"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = self._create_cache_key(func.__name__, args, kwargs)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Check if cached result exists and is valid
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    # Check cache expiration (24 hours)
                    cache_time = datetime.fromisoformat(cached_data.get('timestamp', ''))
                    if (datetime.now() - cache_time).total_seconds() < 86400:
                        logger.info(f"⚡ Using cached result for {func.__name__}")
                        return cached_data['result']
                except Exception as e:
                    logger.warning(f"Cache invalid or expired: {e}")
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Store result in cache
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'function': func.__name__,
                'result': result
            }
            
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Could not cache result: {e}")
            
            return result
        
        return wrapper
    
    def _create_cache_key(self, function_name: str, args: tuple, kwargs: dict) -> str:
        """Create a unique cache key from function arguments"""
        # Convert arguments to string representation
        args_str = "_".join(str(arg) for arg in args)
        kwargs_str = "_".join(f"{k}_{v}" for k, v in sorted(kwargs.items()))
        
        # Create hash for consistent key length
        import hashlib
        combined = f"{function_name}_{args_str}_{kwargs_str}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def parallel_execute(self, tasks: List[Tuple], max_workers: Optional[int] = None) -> List:
        """Execute multiple tasks in parallel"""
        if max_workers is None:
            max_workers = self.max_workers
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {executor.submit(task[0], *task[1], **task[2]): task 
                             for task in tasks if len(task) >= 3}
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append((task, result, None))
                except Exception as e:
                    results.append((task, None, e))
        
        return results
    
    def optimize_file_operations(self, file_list: List[Path], operation: str = 'copy', 
                                target_dir: Optional[Path] = None) -> Dict:
        """Optimize bulk file operations"""
        start_time = time.time()
        success_count = 0
        error_count = 0
        errors = []
        
        # Use parallel processing for large file lists
        if len(file_list) > 10:
            logger.info(f"Using parallel processing for {len(file_list)} files")
            
            # Create tasks
            tasks = []
            for file_path in file_list:
                if operation == 'copy' and target_dir:
                    tasks.append((self._safe_copy, (file_path, target_dir / file_path.name), {}))
                elif operation == 'delete':
                    tasks.append((self._safe_delete, (file_path,), {}))
                elif operation == 'move' and target_dir:
                    tasks.append((self._safe_move, (file_path, target_dir / file_path.name), {}))
            
            # Execute in parallel
            results = self.parallel_execute(tasks)
            
            # Process results
            for task, result, error in results:
                if error:
                    error_count += 1
                    errors.append((task[1][0], str(error)))
                else:
                    success_count += 1
        else:
            # Sequential processing for small lists
            for file_path in file_list:
                try:
                    if operation == 'copy' and target_dir:
                        self._safe_copy(file_path, target_dir / file_path.name)
                    elif operation == 'delete':
                        self._safe_delete(file_path)
                    elif operation == 'move' and target_dir:
                        self._safe_move(file_path, target_dir / file_path.name)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append((file_path, str(e)))
        
        duration = time.time() - start_time
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'duration': duration,
            'errors': errors,
            'success_rate': success_count / len(file_list) if file_list else 0
        }
    
    def _safe_copy(self, source: Path, target: Path) -> bool:
        """Safely copy a file with error handling"""
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            return True
        except Exception as e:
            logger.warning(f"Could not copy {source} to {target}: {e}")
            return False
    
    def _safe_delete(self, file_path: Path) -> bool:
        """Safely delete a file or directory"""
        try:
            if file_path.is_dir():
                shutil.rmtree(file_path)
            else:
                file_path.unlink()
            return True
        except Exception as e:
            logger.warning(f"Could not delete {file_path}: {e}")
            return False
    
    def _safe_move(self, source: Path, target: Path) -> bool:
        """Safely move a file with error handling"""
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            return True
        except Exception as e:
            logger.warning(f"Could not move {source} to {target}: {e}")
            return False
    
    def analyze_performance(self, operation_name: str, start_time: float, 
                           item_count: int, success_count: int) -> Dict:
        """Analyze and log performance metrics"""
        duration = time.time() - start_time
        items_per_second = item_count / duration if duration > 0 else 0
        
        performance_data = {
            'operation': operation_name,
            'duration': duration,
            'item_count': item_count,
            'success_count': success_count,
            'items_per_second': items_per_second,
            'success_rate': success_count / item_count if item_count > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log performance data
        logger.info(f"📊 Performance: {operation_name}")
        logger.info(f"   Duration: {duration:.2f}s")
        logger.info(f"   Items: {item_count}")
        logger.info(f"   Success: {success_count}")
        logger.info(f"   Rate: {items_per_second:.1f} items/s")
        logger.info(f"   Success Rate: {performance_data['success_rate']*100:.1f}%")
        
        return performance_data
    
    def optimize_memory_usage(self, large_data: List) -> List:
        """Optimize memory usage for large datasets"""
        # Process data in chunks if it's very large
        if len(large_data) > 1000:
            chunk_size = 1000
            processed_data = []
            
            for i in range(0, len(large_data), chunk_size):
                chunk = large_data[i:i + chunk_size]
                processed_chunk = self._process_data_chunk(chunk)
                processed_data.extend(processed_chunk)
                
                # Clear memory
                del chunk
                del processed_chunk
            
            return processed_data
        else:
            return self._process_data_chunk(large_data)
    
    def _process_data_chunk(self, data_chunk: List) -> List:
        """Process a chunk of data"""
        # This would contain the actual processing logic
        # For now, just return the chunk as-is
        return data_chunk
    
    def monitor_system_resources(self) -> Dict:
        """Monitor system resource usage"""
        import psutil
        
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_used = memory.used / (1024 ** 3)  # GB
            memory_total = memory.total / (1024 ** 3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_used = disk.used / (1024 ** 3)  # GB
            disk_total = disk.total / (1024 ** 3)  # GB
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'memory_used_gb': memory_used,
                'memory_total_gb': memory_total,
                'disk_usage': disk_usage,
                'disk_used_gb': disk_used,
                'disk_total_gb': disk_total
            }
        except ImportError:
            logger.warning("psutil not available, resource monitoring disabled")
            return {}
        except Exception as e:
            logger.warning(f"Could not monitor system resources: {e}")
            return {}
    
    def profile_function(self, func):
        """Decorator to profile function execution time"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_resources = self.monitor_system_resources()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
            
            end_time = time.time()
            end_resources = self.monitor_system_resources()
            duration = end_time - start_time
            
            # Log profiling information
            logger.info(f"📈 Profiling: {func.__name__}")
            logger.info(f"   Duration: {duration:.3f}s")
            if start_resources and end_resources:
                cpu_diff = end_resources.get('cpu_usage', 0) - start_resources.get('cpu_usage', 0)
                mem_diff = end_resources.get('memory_usage', 0) - start_resources.get('memory_usage', 0)
                logger.info(f"   CPU Δ: {cpu_diff:.1f}%")
                logger.info(f"   Memory Δ: {mem_diff:.1f}%")
            
            if not success:
                logger.error(f"   Error: {error}")
            
            return result
        
        return wrapper
    
    def optimize_network_operations(self, url: str, max_retries: int = 3, 
                                  timeout: int = 30) -> Optional[bytes]:
        """Optimize network operations with retries and caching"""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Create cache key for this URL
        cache_key = hashlib.md5(url.encode('utf-8')).hexdigest()
        cache_file = self.cache_dir / f"network_{cache_key}.cache"
        
        # Check cache first
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = f.read()
                logger.info(f"⚡ Using cached network response for {url}")
                return cached_data
            except Exception:
                pass
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            
            data = response.content
            
            # Cache the response
            try:
                with open(cache_file, 'wb') as f:
                    f.write(data)
            except Exception as e:
                logger.warning(f"Could not cache network response: {e}")
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Network operation failed after {max_retries} retries: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in network operation: {e}")
            return None
    
    def batch_process_files(self, file_paths: List[Path], processor_func, 
                           batch_size: int = 100) -> List:
        """Process files in batches to optimize memory usage"""
        results = []
        
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            batch_results = []
            
            for file_path in batch:
                try:
                    result = processor_func(file_path)
                    batch_results.append((file_path, result, None))
                except Exception as e:
                    batch_results.append((file_path, None, str(e)))
            
            results.extend(batch_results)
            
            # Clear memory
            del batch
            del batch_results
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1) // batch_size}")
        
        return results
    
    def get_performance_recommendations(self, system_info: Dict) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        if not system_info:
            return recommendations
        
        # CPU recommendations
        cpu_usage = system_info.get('cpu_usage', 0)
        if cpu_usage > 80:
            recommendations.append("[INFO] High CPU usage detected. Consider reducing parallel operations.")
        
        # Memory recommendations
        memory_usage = system_info.get('memory_usage', 0)
        if memory_usage > 85:
            recommendations.append("[INFO] High memory usage detected. Consider processing in smaller batches.")
        
        # Disk recommendations
        disk_usage = system_info.get('disk_usage', 0)
        if disk_usage > 90:
            recommendations.append("[INFO] High disk usage detected. Consider cleaning up temporary files.")
        
        # Platform-specific recommendations
        current_platform = platform.system().lower()
        if current_platform == 'windows':
            recommendations.append("[INFO] On Windows, consider using junction points for large file operations.")
        elif current_platform == 'darwin':
            recommendations.append("[INFO] On macOS, consider using hard links for file duplication.")
        elif current_platform == 'linux':
            recommendations.append("[INFO] On Linux, consider using rsync for efficient file operations.")
        
        return recommendations


def optimize_file_copy_operation(source_dir: Path, target_dir: Path, 
                               file_patterns: List[str] = None) -> Dict:
    """Optimized file copy operation with performance monitoring"""
    optimizer = PerformanceOptimizer()
    
    # Find files to copy
    files_to_copy = []
    
    if file_patterns:
        for pattern in file_patterns:
            files_to_copy.extend(source_dir.glob(pattern))
    else:
        files_to_copy = list(source_dir.iterdir())
    
    # Filter out directories
    files_to_copy = [f for f in files_to_copy if f.is_file()]
    
    if not files_to_copy:
        return {'success': True, 'copied': 0, 'duration': 0}
    
    # Start performance monitoring
    start_time = time.time()
    start_resources = optimizer.monitor_system_resources()
    
    # Use optimized file operations
    results = optimizer.optimize_file_operations(
        files_to_copy,
        operation='copy',
        target_dir=target_dir
    )
    
    # End performance monitoring
    end_time = time.time()
    end_resources = optimizer.monitor_system_resources()
    
    # Analyze performance
    performance_data = optimizer.analyze_performance(
        'file_copy',
        start_time,
        len(files_to_copy),
        results['success_count']
    )
    
    # Get recommendations
    recommendations = optimizer.get_performance_recommendations(end_resources)
    
    return {
        'success': results['error_count'] == 0,
        'copied': results['success_count'],
        'failed': results['error_count'],
        'duration': performance_data['duration'],
        'performance': performance_data,
        'recommendations': recommendations,
        'errors': results['errors']
    }


if __name__ == "__main__":
    # Example usage
    optimizer = PerformanceOptimizer()
    
    print("NW.js Automator Performance Optimizer")
    print("=" * 50)
    
    # Monitor system resources
    resources = optimizer.monitor_system_resources()
    print("[System Resources]:")
    if resources:
        print(f"   CPU: {resources['cpu_usage']}%")
        print(f"   Memory: {resources['memory_usage']}% ({resources['memory_used_gb']:.1f}/{resources['memory_total_gb']:.1f} GB)")
        print(f"   Disk: {resources['disk_usage']}% ({resources['disk_used_gb']:.1f}/{resources['disk_total_gb']:.1f} GB)")
    
    # Get recommendations
    recommendations = optimizer.get_performance_recommendations(resources)
    if recommendations:
        print("\n[Performance Recommendations]:")
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print("\n[OK] System resources look good!")