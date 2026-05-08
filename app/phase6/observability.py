from __future__ import annotations

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from functools import wraps
import uuid

from app.config import settings


# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    request_id: str
    timestamp: datetime
    endpoint: str
    method: str
    user_agent: Optional[str]
    ip_address: Optional[str]
    processing_time_ms: float
    phase_timings: Dict[str, float]
    result_count: int
    llm_used: bool
    error: Optional[str]


@dataclass
class MetricsSummary:
    """Summary of metrics over a time period."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_processing_time_ms: float
    llm_usage_rate: float
    top_endpoints: List[Dict[str, Any]]
    error_summary: Dict[str, int]
    time_range: Dict[str, datetime]


class MetricsStore:
    """In-memory store for request metrics."""
    
    def __init__(self):
        self.metrics: List[RequestMetrics] = []
        self.max_size = 10000  # Keep last 10k requests
    
    def add_metric(self, metric: RequestMetrics):
        """Add a new metric to the store."""
        self.metrics.append(metric)
        if len(self.metrics) > self.max_size:
            self.metrics = self.metrics[-self.max_size:]
    
    def get_recent_metrics(self, hours: int = 24) -> List[RequestMetrics]:
        """Get metrics from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics if m.timestamp >= cutoff]


# Global metrics store
metrics_store = MetricsStore()


def log_request(endpoint: str, method: str = "POST", user_agent: str = None, ip_address: str = None):
    """Decorator to log request metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start_time = time.time()
            phase_timings = {}
            
            try:
                # Log request start
                logger.info(json.dumps({
                    "event": "request_start",
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "method": method,
                    "timestamp": datetime.now().isoformat(),
                    "user_agent": user_agent,
                    "ip_address": ip_address
                }))
                
                # Execute function with timing
                result = func(*args, **kwargs)
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Extract result information
                result_count = 0
                llm_used = False
                
                if hasattr(result, 'model_dump'):
                    result_dict = result.model_dump()
                elif isinstance(result, dict):
                    result_dict = result
                else:
                    result_dict = {}
                
                # Count recommendations if available
                if 'recommendations' in result_dict:
                    result_count = len(result_dict['recommendations'])
                elif 'restaurants' in result_dict.get('display', {}):
                    result_count = len(result_dict['display']['restaurants'])
                
                # Check LLM usage
                if 'llm_used' in result_dict:
                    llm_used = result_dict['llm_used']
                elif 'metadata' in result_dict.get('display', {}):
                    llm_used = result_dict['display']['metadata'].get('llm_used', False)
                
                # Create metric
                metric = RequestMetrics(
                    request_id=request_id,
                    timestamp=datetime.now(),
                    endpoint=endpoint,
                    method=method,
                    user_agent=user_agent,
                    ip_address=ip_address,
                    processing_time_ms=processing_time,
                    phase_timings=phase_timings,
                    result_count=result_count,
                    llm_used=llm_used,
                    error=None
                )
                
                metrics_store.add_metric(metric)
                
                # Log request completion
                logger.info(json.dumps({
                    "event": "request_complete",
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "processing_time_ms": processing_time,
                    "result_count": result_count,
                    "llm_used": llm_used,
                    "timestamp": datetime.now().isoformat()
                }))
                
                return result
                
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                
                # Log error
                logger.error(json.dumps({
                    "event": "request_error",
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "error": str(e),
                    "processing_time_ms": processing_time,
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Store error metric
                metric = RequestMetrics(
                    request_id=request_id,
                    timestamp=datetime.now(),
                    endpoint=endpoint,
                    method=method,
                    user_agent=user_agent,
                    ip_address=ip_address,
                    processing_time_ms=processing_time,
                    phase_timings=phase_timings,
                    result_count=0,
                    llm_used=False,
                    error=str(e)
                )
                
                metrics_store.add_metric(metric)
                raise
        
        return wrapper
    return decorator


def log_performance(phase: str, operation: str):
    """Decorator to log performance of specific operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                logger.info(json.dumps({
                    "event": "performance",
                    "phase": phase,
                    "operation": operation,
                    "duration_ms": duration,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }))
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                logger.error(json.dumps({
                    "event": "performance",
                    "phase": phase,
                    "operation": operation,
                    "duration_ms": duration,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }))
                
                raise
        return wrapper
    return decorator


def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log an error with context."""
    error_data = {
        "event": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if context:
        error_data["context"] = context
    
    logger.error(json.dumps(error_data))


def get_metrics(hours: int = 24) -> MetricsSummary:
    """Get metrics summary for the last N hours."""
    recent_metrics = metrics_store.get_recent_metrics(hours)
    
    if not recent_metrics:
        return MetricsSummary(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_processing_time_ms=0.0,
            llm_usage_rate=0.0,
            top_endpoints=[],
            error_summary={},
            time_range={
                "start": datetime.now() - timedelta(hours=hours),
                "end": datetime.now()
            }
        )
    
    total_requests = len(recent_metrics)
    successful_requests = len([m for m in recent_metrics if m.error is None])
    failed_requests = total_requests - successful_requests
    
    # Calculate average processing time
    avg_processing_time = sum(m.processing_time_ms for m in recent_metrics) / total_requests
    
    # Calculate LLM usage rate
    llm_usage_rate = len([m for m in recent_metrics if m.llm_used]) / total_requests
    
    # Top endpoints
    endpoint_counts = {}
    for m in recent_metrics:
        endpoint_counts[m.endpoint] = endpoint_counts.get(m.endpoint, 0) + 1
    
    top_endpoints = [
        {"endpoint": ep, "count": count}
        for ep, count in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Error summary
    error_summary = {}
    for m in recent_metrics:
        if m.error:
            error_type = type(Exception(m.error)).__name__
            error_summary[error_type] = error_summary.get(error_type, 0) + 1
    
    return MetricsSummary(
        total_requests=total_requests,
        successful_requests=successful_requests,
        failed_requests=failed_requests,
        avg_processing_time_ms=avg_processing_time,
        llm_usage_rate=llm_usage_rate,
        top_endpoints=top_endpoints,
        error_summary=error_summary,
        time_range={
            "start": datetime.now() - timedelta(hours=hours),
            "end": datetime.now()
        }
    )


def export_metrics(hours: int = 24) -> Dict[str, Any]:
    """Export metrics in a structured format."""
    summary = get_metrics(hours)
    recent_metrics = metrics_store.get_recent_metrics(hours)
    
    return {
        "summary": asdict(summary),
        "detailed_metrics": [asdict(m) for m in recent_metrics],
        "export_timestamp": datetime.now().isoformat()
    }
