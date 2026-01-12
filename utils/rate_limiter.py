"""Rate limiting utilities for API calls."""

import asyncio
import time
from typing import Optional
from collections import deque
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int
    time_window: float  # in seconds
    retry_delay: float = 2.0
    max_retries: int = 3


class RateLimiter:
    """Thread-safe rate limiter for API calls."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.request_times: deque = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire permission to make a request, waiting if necessary."""
        async with self.lock:
            now = time.time()
            
            # Remove old requests outside the time window
            while self.request_times and self.request_times[0] < now - self.config.time_window:
                self.request_times.popleft()
            
            # Wait if we've exceeded the rate limit
            if len(self.request_times) >= self.config.max_requests:
                sleep_time = self.request_times[0] + self.config.time_window - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    # Clean up again after sleeping
                    now = time.time()
                    while self.request_times and self.request_times[0] < now - self.config.time_window:
                        self.request_times.popleft()
            
            # Record this request
            self.request_times.append(time.time())
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
