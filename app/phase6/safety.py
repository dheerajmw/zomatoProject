from __future__ import annotations

import time
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict, deque
from datetime import datetime, timedelta

from app.config import settings


@dataclass
class SafetyConfig:
    """Configuration for safety measures."""
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000
    max_input_length: int = 1000
    blocked_words: Set[str] = None
    allowed_domains: Set[str] = None
    
    def __post_init__(self):
        if self.blocked_words is None:
            self.blocked_words = {
                'spam', 'abuse', 'hate', 'violence', 'illegal',
                'drugs', 'weapons', 'adult', 'scam'
            }
        if self.allowed_domains is None:
            self.allowed_domains = {'localhost', '127.0.0.1'}


class RateLimiter:
    """Rate limiting implementation using sliding window."""
    
    def __init__(self, config: SafetyConfig):
        self.config = config
        self.requests = defaultdict(lambda: deque())
    
    def is_allowed(self, identifier: str) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed based on rate limits."""
        now = datetime.now()
        user_requests = self.requests[identifier]
        
        # Clean old requests
        cutoff_1min = now - timedelta(minutes=1)
        cutoff_1hour = now - timedelta(hours=1)
        
        # Remove requests older than 1 hour
        while user_requests and user_requests[0] < cutoff_1hour:
            user_requests.popleft()
        
        # Count requests in different time windows
        requests_last_minute = sum(1 for req_time in user_requests if req_time >= cutoff_1min)
        requests_last_hour = len(user_requests)
        
        # Check limits
        if requests_last_minute >= self.config.rate_limit_requests_per_minute:
            return False, {
                "allowed": False,
                "reason": "minute_limit_exceeded",
                "limit": self.config.rate_limit_requests_per_minute,
                "current": requests_last_minute,
                "reset_time": (cutoff_1min + timedelta(minutes=1)).isoformat()
            }
        
        if requests_last_hour >= self.config.rate_limit_requests_per_hour:
            return False, {
                "allowed": False,
                "reason": "hour_limit_exceeded",
                "limit": self.config.rate_limit_requests_per_hour,
                "current": requests_last_hour,
                "reset_time": (cutoff_1hour + timedelta(hours=1)).isoformat()
            }
        
        # Add current request
        user_requests.append(now)
        
        return True, {
            "allowed": True,
            "remaining_minute": self.config.rate_limit_requests_per_minute - requests_last_minute - 1,
            "remaining_hour": self.config.rate_limit_requests_per_hour - requests_last_hour - 1
        }
    
    def get_status(self, identifier: str) -> Dict[str, Any]:
        """Get current rate limit status."""
        now = datetime.now()
        user_requests = self.requests[identifier]
        
        cutoff_1min = now - timedelta(minutes=1)
        cutoff_1hour = now - timedelta(hours=1)
        
        requests_last_minute = sum(1 for req_time in user_requests if req_time >= cutoff_1min)
        requests_last_hour = sum(1 for req_time in user_requests if req_time >= cutoff_1hour)
        
        return {
            "requests_last_minute": requests_last_minute,
            "requests_last_hour": requests_last_hour,
            "limit_per_minute": self.config.rate_limit_requests_per_minute,
            "limit_per_hour": self.config.rate_limit_requests_per_hour,
            "remaining_minute": max(0, self.config.rate_limit_requests_per_minute - requests_last_minute),
            "remaining_hour": max(0, self.config.rate_limit_requests_per_hour - requests_last_hour)
        }


class ContentFilter:
    """Content filtering for user inputs."""
    
    def __init__(self, config: SafetyConfig):
        self.config = config
        self.blocked_patterns = [
            re.compile(r'\b(' + '|'.join(re.escape(word) for word in config.blocked_words) + r')\b', re.IGNORECASE)
        ]
        # Additional patterns for common issues
        self.blocked_patterns.extend([
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),  # Scripts
            re.compile(r'http[s]?://[^\s<>"]+', re.IGNORECASE),  # URLs (optional)
            re.compile(r'[<>]'),  # HTML tags
        ])
    
    def filter_text(self, text: str) -> tuple[bool, Dict[str, Any]]:
        """Filter text content for safety."""
        if not text:
            return True, {"allowed": True, "reason": "empty_input"}
        
        # Length check
        if len(text) > self.config.max_input_length:
            return False, {
                "allowed": False,
                "reason": "input_too_long",
                "max_length": self.config.max_input_length,
                "actual_length": len(text)
            }
        
        # Pattern matching
        blocked_matches = []
        for pattern in self.blocked_patterns:
            matches = pattern.findall(text)
            if matches:
                blocked_matches.extend(matches)
        
        if blocked_matches:
            return False, {
                "allowed": False,
                "reason": "blocked_content",
                "matches": blocked_matches[:5],  # Limit exposure
                "match_count": len(blocked_matches)
            }
        
        return True, {"allowed": True, "reason": "content_safe"}
    
    def filter_preferences(self, preferences: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Filter user preferences for safety."""
        issues = []
        
        # Check location
        location = str(preferences.get('location', '')).strip()
        location_safe, location_result = self.filter_text(location)
        if not location_safe:
            issues.append({"field": "location", "issue": location_result})
        
        # Check cuisines
        cuisines = preferences.get('cuisines', [])
        if isinstance(cuisines, list):
            for i, cuisine in enumerate(cuisines):
                cuisine_safe, cuisine_result = self.filter_text(str(cuisine))
                if not cuisine_safe:
                    issues.append({
                        "field": f"cuisines[{i}]",
                        "issue": cuisine_result
                    })
        
        # Check optional tags
        tags = preferences.get('optional_tags', [])
        if isinstance(tags, list):
            for i, tag in enumerate(tags):
                tag_safe, tag_result = self.filter_text(str(tag))
                if not tag_safe:
                    issues.append({
                        "field": f"optional_tags[{i}]",
                        "issue": tag_result
                    })
        
        if issues:
            return False, {
                "allowed": False,
                "reason": "invalid_preferences",
                "issues": issues
            }
        
        return True, {"allowed": True, "reason": "preferences_safe"}


class TokenLimiter:
    """Token usage limiter for LLM calls."""
    
    def __init__(self, max_tokens_per_minute: int = 10000):
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_usage = deque()
    
    def consume_tokens(self, token_count: int) -> tuple[bool, Dict[str, Any]]:
        """Consume tokens and check limits."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Clean old usage
        while self.token_usage and self.token_usage[0][0] < cutoff:
            self.token_usage.popleft()
        
        # Calculate current usage
        current_usage = sum(tokens for _, tokens in self.token_usage)
        
        if current_usage + token_count > self.max_tokens_per_minute:
            return False, {
                "allowed": False,
                "reason": "token_limit_exceeded",
                "current_usage": current_usage,
                "requested": token_count,
                "limit": self.max_tokens_per_minute,
                "reset_time": (cutoff + timedelta(minutes=1)).isoformat()
            }
        
        # Record usage
        self.token_usage.append((now, token_count))
        
        return True, {
            "allowed": True,
            "remaining_tokens": self.max_tokens_per_minute - current_usage - token_count,
            "current_usage": current_usage + token_count
        }
    
    def get_usage_status(self) -> Dict[str, Any]:
        """Get current token usage status."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Clean old usage
        while self.token_usage and self.token_usage[0][0] < cutoff:
            self.token_usage.popleft()
        
        current_usage = sum(tokens for _, tokens in self.token_usage)
        
        return {
            "current_usage": current_usage,
            "limit": self.max_tokens_per_minute,
            "remaining": max(0, self.max_tokens_per_minute - current_usage),
            "reset_time": (cutoff + timedelta(minutes=1)).isoformat()
        }


# Global safety components
safety_config = SafetyConfig()
rate_limiter = RateLimiter(safety_config)
content_filter = ContentFilter(safety_config)
token_limiter = TokenLimiter()


def check_rate_limit(identifier: str) -> tuple[bool, Dict[str, Any]]:
    """Check rate limit for an identifier."""
    return rate_limiter.is_allowed(identifier)


def filter_content(text: str) -> tuple[bool, Dict[str, Any]]:
    """Filter text content."""
    return content_filter.filter_text(text)


def filter_preferences(preferences: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """Filter user preferences."""
    return content_filter.filter_preferences(preferences)


def check_token_limit(token_count: int) -> tuple[bool, Dict[str, Any]]:
    """Check token usage limits."""
    return token_limiter.consume_tokens(token_count)


def get_safety_status(identifier: str = None) -> Dict[str, Any]:
    """Get comprehensive safety status."""
    status = {
        "rate_limits": rate_limiter.get_status(identifier) if identifier else {},
        "token_limits": token_limiter.get_usage_status(),
        "config": {
            "max_input_length": safety_config.max_input_length,
            "rate_limits_per_minute": safety_config.rate_limit_requests_per_minute,
            "rate_limits_per_hour": safety_config.rate_limit_requests_per_hour,
            "blocked_words_count": len(safety_config.blocked_words)
        }
    }
    return status
