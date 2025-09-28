"""
Async utilities and helpers for improved performance
"""

import asyncio
import httpx
from typing import List, Callable, Any, Dict
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import time

# Thread pool for CPU-intensive tasks
thread_pool = ThreadPoolExecutor(max_workers=4)

async def run_in_thread_pool(func: Callable, *args, **kwargs) -> Any:
    """Run a CPU-intensive function in a thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(thread_pool, func, *args, **kwargs)

async def gather_with_concurrency(tasks: List, max_concurrency: int = 10) -> List[Any]:
    """Run tasks with limited concurrency"""
    semaphore = asyncio.Semaphore(max_concurrency)

    async def _run_with_semaphore(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*[_run_with_semaphore(task) for task in tasks])

class AsyncBatch:
    """Batch processor for async operations"""

    def __init__(self, batch_size: int = 10, max_wait_time: float = 0.1):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_items: List[tuple] = []
        self.results: Dict[str, Any] = {}
        self._processing = False

    async def add_item(self, item_id: str, item_data: Any) -> Any:
        """Add item to batch and return result when ready"""
        self.pending_items.append((item_id, item_data))

        # Start processing if batch is full or not already processing
        if len(self.pending_items) >= self.batch_size or not self._processing:
            await self._process_batch()

        # Wait for result
        while item_id not in self.results:
            await asyncio.sleep(0.01)

        result = self.results.pop(item_id)
        return result

    async def _process_batch(self):
        """Process current batch of items"""
        if self._processing or not self.pending_items:
            return

        self._processing = True
        try:
            # Get items to process
            items_to_process = self.pending_items[:self.batch_size]
            self.pending_items = self.pending_items[self.batch_size:]

            # Process items (override in subclass)
            results = await self._process_items(items_to_process)

            # Store results
            for (item_id, _), result in zip(items_to_process, results):
                self.results[item_id] = result

        finally:
            self._processing = False

    async def _process_items(self, items: List) -> List[Any]:
        """Override this method to implement batch processing logic"""
        return [item_data for item_id, item_data in items]

class ConnectionPool:
    """HTTP connection pool for external API calls"""

    def __init__(self, max_connections: int = 10, timeout: float = 30.0):
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=max_connections),
            timeout=httpx.Timeout(timeout)
        )

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Make GET request with connection pooling"""
        return await self.client.get(url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Make POST request with connection pooling"""
        return await self.client.post(url, **kwargs)

    async def close(self):
        """Close the connection pool"""
        await self.client.aclose()

# Global connection pool instance
connection_pool = ConnectionPool()

def async_cached(ttl: int = 300):
    """Decorator for caching async function results with TTL"""
    cache: Dict[str, tuple] = {}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    return result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())

            # Cleanup old cache entries periodically
            if len(cache) > 1000:
                current_time = time.time()
                expired_keys = [
                    key for key, (_, timestamp) in cache.items()
                    if current_time - timestamp > ttl
                ]
                for key in expired_keys:
                    del cache[key]

            return result
        return wrapper
    return decorator

async def timeout_after(seconds: float, coro):
    """Add timeout to coroutine"""
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

class BackgroundTaskManager:
    """Manager for background tasks"""

    def __init__(self):
        self.tasks = set()

    def create_task(self, coro, name: str | None = None):
        """Create and track background task"""
        task = asyncio.create_task(coro, name=name)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    async def wait_all(self, timeout: float | None = None):
        """Wait for all background tasks to complete"""
        if self.tasks:
            await asyncio.wait(self.tasks, timeout=timeout)

    def cancel_all(self):
        """Cancel all background tasks"""
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()

# Global task manager
task_manager = BackgroundTaskManager()