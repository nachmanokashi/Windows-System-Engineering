import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.event_sourcing.events import BaseEvent, AggregateType, EventType


class EventStore:
    """
    Event Store - מנהל את כל האירועים במערכת
    
    תפקידים:
    1. שמירת אירועים לטבלת events
    2. קריאת אירועים מהטבלה
    3. Replay - בניית State מאירועים
    4. Snapshots לביצועים
    """
    
    def __init__(self, db: Session):
        """
        Args:
            db: Session של SQLAlchemy
        """
        self.db = db
    
    # ============================================
    # שמירת אירועים
    # ============================================
    
    def save_event(self, event: BaseEvent) -> int:
        """
        שמירת אירוע לטבלת events
        
        Args:
            event: אובייקט Event לשמירה
            
        Returns:
            event_id: ה-ID של האירוע שנשמר
            
        Example:
            >>> event = ArticleCreatedEvent(article_id=1, title="Test", ...)
            >>> event_id = event_store.save_event(event)
            >>> print(f"Event saved with ID: {event_id}")
        """
        # המר את ה-Enums לstring
        event_type_str = event.event_type.value if isinstance(event.event_type, EventType) else event.event_type
        aggregate_type_str = event.aggregate_type.value if isinstance(event.aggregate_type, AggregateType) else event.aggregate_type
        
        # INSERT query עם OUTPUT
        insert_query = text("""
            INSERT INTO events (
                event_type, 
                aggregate_id, 
                aggregate_type, 
                event_data, 
                metadata,
                user_id, 
                version
            )
            OUTPUT INSERTED.id
            VALUES (
                :event_type, 
                :aggregate_id, 
                :aggregate_type, 
                :event_data,
                :metadata,
                :user_id, 
                :version
            )
        """)
        
        result = self.db.execute(insert_query, {
            "event_type": event_type_str,
            "aggregate_id": event.aggregate_id,
            "aggregate_type": aggregate_type_str,
            "event_data": json.dumps(event.event_data, ensure_ascii=False),
            "metadata": json.dumps(event.metadata, ensure_ascii=False) if event.metadata else None,
            "user_id": event.user_id,
            "version": event.version
        })
        
        # קבל את ה-ID
        event_id = result.scalar()
        
        # Commit
        self.db.commit()
        
        return int(event_id) if event_id else 0
    
    # ============================================
    # קריאת אירועים
    # ============================================
    
    def get_events_by_aggregate(
        self, 
        aggregate_type: str, 
        aggregate_id: int
    ) -> List[Dict[str, Any]]:
        """
        קבלת כל האירועים של aggregate מסוים
        
        Args:
            aggregate_type: סוג הישות (Article, User, Like)
            aggregate_id: ID של הישות
            
        Returns:
            רשימת אירועים
            
        Example:
            >>> events = event_store.get_events_by_aggregate("Article", 1)
            >>> print(f"Found {len(events)} events for Article 1")
        """
        query = text("""
            SELECT 
                id,
                event_type,
                aggregate_id,
                aggregate_type,
                event_data,
                metadata,
                user_id,
                created_at,
                version
            FROM events
            WHERE aggregate_type = :aggregate_type 
              AND aggregate_id = :aggregate_id
            ORDER BY created_at ASC, version ASC
        """)
        
        result = self.db.execute(query, {
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id
        })
        
        events = []
        for row in result:
            events.append({
                "id": row.id,
                "event_type": row.event_type,
                "aggregate_id": row.aggregate_id,
                "aggregate_type": row.aggregate_type,
                "event_data": json.loads(row.event_data) if row.event_data else {},
                "metadata": json.loads(row.metadata) if row.metadata else None,
                "user_id": row.user_id,
                "created_at": row.created_at,
                "version": row.version
            })
        
        return events
    
    def get_events_since(self, since_event_id: int = 0, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        קבלת אירועים מאז event_id מסוים
        שימושי ל-Event Handlers
        
        Args:
            since_event_id: ID של אירוע אחרון שעובד
            limit: מקסימום אירועים להחזיר
            
        Returns:
            רשימת אירועים חדשים
        """
        query = text("""
            SELECT TOP :limit
                id,
                event_type,
                aggregate_id,
                aggregate_type,
                event_data,
                metadata,
                user_id,
                created_at,
                version
            FROM events
            WHERE id > :since_event_id
            ORDER BY id ASC
        """)
        
        result = self.db.execute(query, {
            "since_event_id": since_event_id,
            "limit": limit
        })
        
        events = []
        for row in result:
            events.append({
                "id": row.id,
                "event_type": row.event_type,
                "aggregate_id": row.aggregate_id,
                "aggregate_type": row.aggregate_type,
                "event_data": json.loads(row.event_data) if row.event_data else {},
                "metadata": json.loads(row.metadata) if row.metadata else None,
                "user_id": row.user_id,
                "created_at": row.created_at,
                "version": row.version
            })
        
        return events
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        קבלת אירועים לפי סוג
        
        Args:
            event_type: סוג האירוע (ArticleCreated, UserLoggedIn, etc.)
            limit: מקסימום אירועים
            
        Returns:
            רשימת אירועים
        """
        query = text("""
            SELECT TOP :limit
                id,
                event_type,
                aggregate_id,
                aggregate_type,
                event_data,
                metadata,
                user_id,
                created_at,
                version
            FROM events
            WHERE event_type = :event_type
            ORDER BY created_at DESC
        """)
        
        result = self.db.execute(query, {
            "event_type": event_type,
            "limit": limit
        })
        
        events = []
        for row in result:
            events.append({
                "id": row.id,
                "event_type": row.event_type,
                "aggregate_id": row.aggregate_id,
                "aggregate_type": row.aggregate_type,
                "event_data": json.loads(row.event_data) if row.event_data else {},
                "metadata": json.loads(row.metadata) if row.metadata else None,
                "user_id": row.user_id,
                "created_at": row.created_at,
                "version": row.version
            })
        
        return events
    
    def get_latest_event_id(self) -> int:
        """
        קבלת ה-ID של האירוע האחרון
        שימושי לEvent Handlers
        
        Returns:
            ID של האירוע האחרון, או 0 אם אין אירועים
        """
        query = text("SELECT MAX(id) as max_id FROM events")
        result = self.db.execute(query)
        row = result.fetchone()
        return row.max_id if row and row.max_id else 0
    
    # ============================================
    # Replay - בניית State מאירועים
    # ============================================
    
    def replay_events(
        self, 
        aggregate_type: str, 
        aggregate_id: int
    ) -> Dict[str, Any]:
        """
        Replay - בניית State מכל האירועים
        
        זה הקסם של Event Sourcing!
        במקום לקרוא את המצב הנוכחי מהטבלה,
        אנחנו בונים אותו מכל האירועים שקרו.
        
        Args:
            aggregate_type: סוג הישות
            aggregate_id: ID של הישות
            
        Returns:
            State המלא של הישות
            
        Example:
            >>> state = event_store.replay_events("Article", 1)
            >>> print(state["title"])  # כותרת המאמר
        """
        events = self.get_events_by_aggregate(aggregate_type, aggregate_id)
        
        state = {}
        
        # עבור על כל אירוע ובנה את ה-State
        for event in events:
            event_type = event["event_type"]
            event_data = event["event_data"]
            
            # Article Events
            if event_type == "ArticleCreated":
                state = event_data.copy()
                state["id"] = aggregate_id
                state["is_deleted"] = False
            
            elif event_type == "ArticleUpdated":
                updated_fields = event_data.get("updated_fields", {})
                state.update(updated_fields)
            
            elif event_type == "ArticleDeleted":
                state["is_deleted"] = True
                state["deleted_at"] = event_data.get("deleted_at")
            
            # User Events
            elif event_type == "UserRegistered":
                state = event_data.copy()
                state["id"] = aggregate_id
                state["is_active"] = True
            
            elif event_type == "UserUpdated":
                updated_fields = event_data.get("updated_fields", {})
                state.update(updated_fields)
        
        return state
    
    def save_snapshot(
        self, 
        aggregate_type: str, 
        aggregate_id: int, 
        state: Dict[str, Any],
        version: int
    ) -> int:
        """
        שמירת Snapshot של State
        
        Snapshot זה "תמונת מצב" של הישות.
        במקום לעבור על 1000 אירועים, אפשר לקרוא Snapshot
        ואז רק את האירועים שאחריו.
        
        Args:
            aggregate_type: סוג הישות
            aggregate_id: ID של הישות
            state: ה-State המלא לשמירה
            version: גרסה של ה-Snapshot
            
        Returns:
            snapshot_id: ID של ה-Snapshot
        """
        query = text("""
            INSERT INTO snapshots (
                aggregate_type,
                aggregate_id,
                state_data,
                version
            )
            VALUES (
                :aggregate_type,
                :aggregate_id,
                :state_data,
                :version
            );
            SELECT SCOPE_IDENTITY() as snapshot_id;
        """)
        
        result = self.db.execute(query, {
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
            "state_data": json.dumps(state, ensure_ascii=False),
            "version": version
        })
        
        self.db.commit()
        
        snapshot_id = result.scalar()
        return int(snapshot_id) if snapshot_id else 0
    
    def get_latest_snapshot(
        self, 
        aggregate_type: str, 
        aggregate_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        קבלת ה-Snapshot האחרון
        
        Returns:
            Snapshot או None אם אין
        """
        query = text("""
            SELECT TOP 1
                state_data,
                version,
                created_at
            FROM snapshots
            WHERE aggregate_type = :aggregate_type
              AND aggregate_id = :aggregate_id
            ORDER BY version DESC
        """)
        
        result = self.db.execute(query, {
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id
        })
        
        row = result.fetchone()
        
        if row:
            return {
                "state": json.loads(row.state_data),
                "version": row.version,
                "created_at": row.created_at
            }
        
        return None


# ============================================
# Helper Functions
# ============================================

def get_event_store(db: Session) -> EventStore:
    """
    Factory function לקבלת Event Store
    
    Args:
        db: Database session
        
    Returns:
        EventStore instance
        
    Usage:
        from app.event_sourcing.event_store import get_event_store
        
        event_store = get_event_store(db)
        event_store.save_event(event)
    """
    return EventStore(db)