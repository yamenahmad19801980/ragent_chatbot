"""
Performance monitoring utilities for the ragent_chatbot project.
Provides metrics collection, analysis, and reporting.
"""

import time
import asyncio
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from threading import Lock
from utils.logger import get_logger


@dataclass
class PerformanceMetric:
    """Represents a single performance metric."""
    operation: str
    duration: float
    timestamp: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """Performance statistics for an operation."""
    operation: str
    count: int
    total_duration: float
    avg_duration: float
    min_duration: float
    max_duration: float
    median_duration: float
    success_rate: float
    p95_duration: float
    p99_duration: float


class PerformanceMonitor:
    """Centralized performance monitoring system."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, max_metrics: int = 10000):
        if hasattr(self, '_initialized'):
            return
        
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.logger = get_logger(__name__)
        self._initialized = True
    
    def record_metric(self, operation: str, duration: float, success: bool = True, 
                     metadata: Optional[Dict[str, Any]] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=time.time(),
            success=success,
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        self.logger.debug(f"Recorded metric: {operation} - {duration:.3f}s")
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, PerformanceStats]:
        """Get performance statistics for operations."""
        if operation:
            filtered_metrics = [m for m in self.metrics if m.operation == operation]
        else:
            filtered_metrics = list(self.metrics)
        
        if not filtered_metrics:
            return {}
        
        # Group by operation
        operation_groups = defaultdict(list)
        for metric in filtered_metrics:
            operation_groups[metric.operation].append(metric)
        
        stats = {}
        for op, metrics in operation_groups.items():
            durations = [m.duration for m in metrics]
            successes = [m.success for m in metrics]
            
            stats[op] = PerformanceStats(
                operation=op,
                count=len(metrics),
                total_duration=sum(durations),
                avg_duration=statistics.mean(durations),
                min_duration=min(durations),
                max_duration=max(durations),
                median_duration=statistics.median(durations),
                success_rate=sum(successes) / len(successes),
                p95_duration=self._percentile(durations, 95),
                p99_duration=self._percentile(durations, 99)
            )
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a list of numbers."""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def get_slowest_operations(self, limit: int = 10) -> List[PerformanceMetric]:
        """Get the slowest operations."""
        return sorted(self.metrics, key=lambda x: x.duration, reverse=True)[:limit]
    
    def get_failed_operations(self) -> List[PerformanceMetric]:
        """Get all failed operations."""
        return [m for m in self.metrics if not m.success]
    
    def clear_metrics(self):
        """Clear all recorded metrics."""
        self.metrics.clear()
        self.logger.info("Performance metrics cleared")
    
    def export_metrics(self) -> List[Dict[str, Any]]:
        """Export metrics as dictionaries."""
        return [
            {
                "operation": m.operation,
                "duration": m.duration,
                "timestamp": m.timestamp,
                "success": m.success,
                "metadata": m.metadata
            }
            for m in self.metrics
        ]


def performance_timer(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Decorator for timing function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                monitor.record_metric(operation_name, duration, success, metadata)
        
        return wrapper
    return decorator


def async_performance_timer(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Decorator for timing async function execution."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                monitor.record_metric(operation_name, duration, success, metadata)
        
        return wrapper
    return decorator


class PerformanceComparison:
    """Utility for comparing performance between sync and async operations."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def compare_operations(self, sync_func: Callable, async_func: Callable, 
                               *args, **kwargs) -> Dict[str, Any]:
        """Compare performance between sync and async operations."""
        results = {}
        
        # Test sync operation
        sync_start = time.time()
        try:
            sync_result = sync_func(*args, **kwargs)
            sync_success = True
        except Exception as e:
            sync_result = None
            sync_success = False
            self.logger.error(f"Sync operation failed: {e}")
        finally:
            sync_duration = time.time() - sync_start
        
        # Test async operation
        async_start = time.time()
        try:
            async_result = await async_func(*args, **kwargs)
            async_success = True
        except Exception as e:
            async_result = None
            async_success = False
            self.logger.error(f"Async operation failed: {e}")
        finally:
            async_duration = time.time() - async_start
        
        # Calculate improvement
        if sync_duration > 0:
            improvement = ((sync_duration - async_duration) / sync_duration) * 100
        else:
            improvement = 0
        
        results = {
            "sync": {
                "duration": sync_duration,
                "success": sync_success,
                "result": sync_result
            },
            "async": {
                "duration": async_duration,
                "success": async_success,
                "result": async_result
            },
            "improvement_percent": improvement,
            "faster_operation": "async" if async_duration < sync_duration else "sync"
        }
        
        self.logger.info(f"Performance comparison: Sync {sync_duration:.3f}s, "
                        f"Async {async_duration:.3f}s, Improvement: {improvement:.1f}%")
        
        return results
    
    def generate_report(self, monitor: PerformanceMonitor) -> str:
        """Generate a performance report."""
        stats = monitor.get_stats()
        
        if not stats:
            return "No performance data available."
        
        report = ["Performance Report", "=" * 50]
        
        for operation, stat in stats.items():
            report.append(f"\nOperation: {operation}")
            report.append(f"  Count: {stat.count}")
            report.append(f"  Total Duration: {stat.total_duration:.3f}s")
            report.append(f"  Average Duration: {stat.avg_duration:.3f}s")
            report.append(f"  Min Duration: {stat.min_duration:.3f}s")
            report.append(f"  Max Duration: {stat.max_duration:.3f}s")
            report.append(f"  Median Duration: {stat.median_duration:.3f}s")
            report.append(f"  95th Percentile: {stat.p95_duration:.3f}s")
            report.append(f"  99th Percentile: {stat.p99_duration:.3f}s")
            report.append(f"  Success Rate: {stat.success_rate:.1%}")
        
        # Add slowest operations
        slowest = monitor.get_slowest_operations(5)
        if slowest:
            report.append(f"\nSlowest Operations:")
            for metric in slowest:
                report.append(f"  {metric.operation}: {metric.duration:.3f}s")
        
        # Add failed operations
        failed = monitor.get_failed_operations()
        if failed:
            report.append(f"\nFailed Operations: {len(failed)}")
        
        return "\n".join(report)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Convenience functions
def record_metric(operation: str, duration: float, success: bool = True, 
                 metadata: Optional[Dict[str, Any]] = None):
    """Record a performance metric."""
    performance_monitor.record_metric(operation, duration, success, metadata)


def get_performance_stats(operation: Optional[str] = None) -> Dict[str, PerformanceStats]:
    """Get performance statistics."""
    return performance_monitor.get_stats(operation)


def clear_performance_metrics():
    """Clear all performance metrics."""
    performance_monitor.clear_metrics()


def export_performance_metrics() -> List[Dict[str, Any]]:
    """Export performance metrics."""
    return performance_monitor.export_metrics()
