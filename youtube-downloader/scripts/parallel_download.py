#!/usr/bin/env python3
"""Perform multiple downloads in parallel, with a decorator to allow retries."""

import time
import random
import concurrent.futures
from functools import wraps
from dataclasses import dataclass
from collections.abc import Callable


@dataclass
class Result:
    """A download result."""
    url: str
    success: bool
    filepath: object|None = None
    error: Exception|None = None


def with_retry(max_retries: int = 3, retry_delay: float = 1.0, retry_on_exceptions: list[type[Exception]]|None = None):
    """Decorator that adds retry logic to a download function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise
                    if retry_on_exceptions and not any(isinstance(e, exc_type) for exc_type in retry_on_exceptions):
                        raise
                    wait_time = retry_delay * (2 ** attempt) + random.uniform(0, 0.5)
                    time.sleep(wait_time)
        return wrapper
    return decorator


def parallel_download(urls: list[str], func: Callable[[str], object|None], max_workers: int = 5) -> list[Result]:
    """Download multiple URLs in parallel."""
    results = []
    
    def download(url: str) -> Result:
        try:
            filepath = func(url).resolve()
            return Result(url=url, success=True, filepath=filepath)
        except Exception as e:
            return Result(url=url, success=False, error=e)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    return results
