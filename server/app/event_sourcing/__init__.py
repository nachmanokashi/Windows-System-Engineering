# server/app/event_sourcing/__init__.py
"""
Event Sourcing Module
"""

from .events import (
    BaseEvent,
    EventType,
    AggregateType,
    ArticleCreatedEvent,
    ArticleUpdatedEvent,
    ArticleDeletedEvent,
    ArticleViewedEvent,
    UserRegisteredEvent,
    UserLoggedInEvent,
    UserLoggedOutEvent,
    UserUpdatedEvent,
    ArticleLikedEvent,
    ArticleDislikedEvent,
    LikeRemovedEvent
)

from .event_store import EventStore, get_event_store

__all__ = [
    # Events
    "BaseEvent",
    "EventType",
    "AggregateType",
    "ArticleCreatedEvent",
    "ArticleUpdatedEvent",
    "ArticleDeletedEvent",
    "ArticleViewedEvent",
    "UserRegisteredEvent",
    "UserLoggedInEvent",
    "UserLoggedOutEvent",
    "UserUpdatedEvent",
    "ArticleLikedEvent",
    "ArticleDislikedEvent",
    "LikeRemovedEvent",
    
    # Event Store
    "EventStore",
    "get_event_store"
]