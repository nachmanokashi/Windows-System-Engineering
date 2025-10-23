from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


# ============================================
# Enums - הגדרות קבועות
# ============================================

class AggregateType(str, Enum):
    """סוגי Aggregates במערכת"""
    ARTICLE = "Article"
    USER = "User"
    LIKE = "Like"


class EventType(str, Enum):
    """סוגי אירועים במערכת"""
    # Article Events
    ARTICLE_CREATED = "ArticleCreated"
    ARTICLE_UPDATED = "ArticleUpdated"
    ARTICLE_DELETED = "ArticleDeleted"
    ARTICLE_VIEWED = "ArticleViewed"
    
    # User Events
    USER_REGISTERED = "UserRegistered"
    USER_LOGGED_IN = "UserLoggedIn"
    USER_LOGGED_OUT = "UserLoggedOut"
    USER_UPDATED = "UserUpdated"
    
    # Like Events
    ARTICLE_LIKED = "ArticleLiked"
    ARTICLE_DISLIKED = "ArticleDisliked"
    LIKE_REMOVED = "LikeRemoved"


# ============================================
# Base Event Class
# ============================================

class BaseEvent(BaseModel):
    """
    Base class לכל האירועים
    כל אירוע יורש ממחלקה זו
    """
    event_type: EventType
    aggregate_id: int
    aggregate_type: AggregateType
    event_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    version: int = 1
    
    class Config:
        use_enum_values = True


# ============================================
# Article Events - אירועים הקשורים למאמרים
# ============================================

class ArticleCreatedEvent(BaseEvent):
    """
    אירוע יצירת מאמר חדש
    נשמר כשיוצרים מאמר חדש במערכת
    """
    
    def __init__(
        self, 
        article_id: int, 
        title: str, 
        summary: str, 
        url: str, 
        image_url: str, 
        category: str, 
        content: Optional[str] = None, 
        source: Optional[str] = None,
        user_id: Optional[int] = None, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.ARTICLE_CREATED,
            aggregate_id=article_id,
            aggregate_type=AggregateType.ARTICLE,
            event_data={
                "title": title,
                "summary": summary,
                "url": url,
                "image_url": image_url,
                "category": category,
                "content": content,
                "source": source,
                "created_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


class ArticleUpdatedEvent(BaseEvent):
    """
    אירוע עדכון מאמר
    נשמר כשמעדכנים פרטי מאמר
    """
    
    def __init__(
        self, 
        article_id: int, 
        updated_fields: Dict[str, Any],
        user_id: Optional[int] = None, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.ARTICLE_UPDATED,
            aggregate_id=article_id,
            aggregate_type=AggregateType.ARTICLE,
            event_data={
                "updated_fields": updated_fields,
                "updated_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


class ArticleDeletedEvent(BaseEvent):
    """
    אירוע מחיקת מאמר
    """
    
    def __init__(
        self, 
        article_id: int, 
        user_id: Optional[int] = None, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.ARTICLE_DELETED,
            aggregate_id=article_id,
            aggregate_type=AggregateType.ARTICLE,
            event_data={
                "deleted_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


class ArticleViewedEvent(BaseEvent):
    """
    אירוע צפייה במאמר
    נשמר כל פעם שמשתמש צופה במאמר
    """
    
    def __init__(
        self, 
        article_id: int, 
        user_id: Optional[int] = None, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.ARTICLE_VIEWED,
            aggregate_id=article_id,
            aggregate_type=AggregateType.ARTICLE,
            event_data={
                "viewed_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


# ============================================
# User Events - אירועים הקשורים למשתמשים
# ============================================

class UserRegisteredEvent(BaseEvent):
    """
    אירוע רישום משתמש חדש
    """
    
    def __init__(
        self, 
        user_id: int, 
        username: str, 
        email: str,
        full_name: Optional[str] = None, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.USER_REGISTERED,
            aggregate_id=user_id,
            aggregate_type=AggregateType.USER,
            event_data={
                "username": username,
                "email": email,
                "full_name": full_name,
                "registered_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


class UserLoggedInEvent(BaseEvent):
    """
    אירוע התחברות משתמש
    """
    
    def __init__(
        self, 
        user_id: int, 
        ip_address: Optional[str] = None, 
        user_agent: Optional[str] = None, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.USER_LOGGED_IN,
            aggregate_id=user_id,
            aggregate_type=AggregateType.USER,
            event_data={
                "logged_in_at": datetime.now().isoformat()
            },
            metadata={
                "ip_address": ip_address,
                "user_agent": user_agent
            },
            user_id=user_id,
            **kwargs
        )


class UserLoggedOutEvent(BaseEvent):
    """
    אירוע יציאה של משתמש
    """
    
    def __init__(
        self, 
        user_id: int, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.USER_LOGGED_OUT,
            aggregate_id=user_id,
            aggregate_type=AggregateType.USER,
            event_data={
                "logged_out_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


class UserUpdatedEvent(BaseEvent):
    """
    אירוע עדכון פרטי משתמש
    """
    
    def __init__(
        self, 
        user_id: int, 
        updated_fields: Dict[str, Any], 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.USER_UPDATED,
            aggregate_id=user_id,
            aggregate_type=AggregateType.USER,
            event_data={
                "updated_fields": updated_fields,
                "updated_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


# ============================================
# Like Events - אירועים של לייקים
# ============================================

class ArticleLikedEvent(BaseEvent):
    """
    אירוע לייק למאמר
    """
    
    def __init__(
        self, 
        like_id: int, 
        article_id: int, 
        user_id: int, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.ARTICLE_LIKED,
            aggregate_id=like_id,
            aggregate_type=AggregateType.LIKE,
            event_data={
                "article_id": article_id,
                "user_id": user_id,
                "liked_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


class ArticleDislikedEvent(BaseEvent):

    
    def __init__(
        self, 
        like_id: int, 
        article_id: int, 
        user_id: int, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.ARTICLE_DISLIKED,
            aggregate_id=like_id,
            aggregate_type=AggregateType.LIKE,
            event_data={
                "article_id": article_id,
                "user_id": user_id,
                "disliked_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )


class LikeRemovedEvent(BaseEvent):
    
    def __init__(
        self, 
        like_id: int, 
        article_id: int, 
        user_id: int, 
        **kwargs
    ):
        super().__init__(
            event_type=EventType.LIKE_REMOVED,
            aggregate_id=like_id,
            aggregate_type=AggregateType.LIKE,
            event_data={
                "article_id": article_id,
                "user_id": user_id,
                "removed_at": datetime.now().isoformat()
            },
            user_id=user_id,
            **kwargs
        )