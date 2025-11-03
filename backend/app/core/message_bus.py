"""
Lightweight in-memory message bus for inter-agent communication.

Provides pub/sub messaging with topics. Pluggable for Redis/Kafka in production.
"""

from typing import Dict, List, Callable, Any, Awaitable
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class MessageBus:
    """
    In-memory pub/sub message bus.
    
    Supports:
    - Topic-based pub/sub
    - Async message handlers
    - Blocking vs non-blocking publish
    - Subscriber management
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def subscribe(self, topic: str, handler: Callable[[Any], Awaitable[None]]):
        """Subscribe to a topic with an async handler."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
        logger.info(f"Subscribed handler to topic: {topic}")
    
    def unsubscribe(self, topic: str, handler: Callable):
        """Unsubscribe a handler from a topic."""
        if topic in self._subscribers:
            try:
                self._subscribers[topic].remove(handler)
                logger.info(f"Unsubscribed handler from topic: {topic}")
            except ValueError:
                pass
    
    async def publish(self, topic: str, message: Any, block: bool = False):
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            message: Message payload (dict, Pydantic model, etc.)
            block: If True, wait for all handlers to complete
        """
        if topic not in self._subscribers:
            return
        
        handlers = self._subscribers[topic].copy()
        
        if block:
            # Wait for all handlers
            tasks = [handler(message) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Fire and forget (run in background)
            for handler in handlers:
                asyncio.create_task(self._run_handler(handler, message))
    
    async def _run_handler(self, handler: Callable, message: Any):
        """Run a handler in the background."""
        try:
            await handler(message)
        except Exception as e:
            logger.error(f"Handler error for message on topic: {e}")
    
    def get_topic_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for a topic."""
        return len(self._subscribers.get(topic, []))
    
    def list_topics(self) -> List[str]:
        """List all topics with subscribers."""
        return list(self._subscribers.keys())
    
    def clear_topic(self, topic: str):
        """Remove all subscribers from a topic."""
        if topic in self._subscribers:
            del self._subscribers[topic]
            logger.info(f"Cleared all subscribers from topic: {topic}")
    
    def shutdown(self):
        """Shutdown the message bus."""
        self._executor.shutdown(wait=False)
        self._subscribers.clear()
        logger.info("Message bus shutdown")


# Singleton instance
_message_bus: MessageBus = None


def get_message_bus() -> MessageBus:
    """Get or create the global message bus instance."""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus

