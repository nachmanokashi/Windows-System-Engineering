import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.event_sourcing.events import BaseEvent, AggregateType, EventType


class EventStore:
    # מחלקה שמנהלת אירועים (Event Sourcing)
    def __init__(self, db: Session):
        self.db = db

    # שמירת אירוע במסד הנתונים
    def save_event(self, event: BaseEvent) -> int:
        event_type_str = event.event_type.value if isinstance(event.event_type, EventType) else event.event_type
        aggregate_type_str = event.aggregate_type.value if isinstance(event.aggregate_type, AggregateType) else event.aggregate_type

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

        event_id = result.scalar()
        self.db.commit()
        return int(event_id) if event_id else 0

    # קבלת אירועים לפי מזהה וסוג ישות
    def get_events_by_aggregate(self, aggregate_type: str, aggregate_id: int) -> List[Dict[str, Any]]:
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

    # קבלת אירועים מה-ID האחרון
    def get_events_since(self, since_event_id: int = 0, limit: int = 1000) -> List[Dict[str, Any]]:
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

    # קבלת אירועים לפי סוג
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
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

    # קבלת ID של האירוע האחרון
    def get_latest_event_id(self) -> int:
        query = text("SELECT MAX(id) as max_id FROM events")
        result = self.db.execute(query)
        row = result.fetchone()
        return row.max_id if row and row.max_id else 0

    # בניית מצב (State) מחדש מכל האירועים
    def replay_events(self, aggregate_type: str, aggregate_id: int) -> Dict[str, Any]:
        events = self.get_events_by_aggregate(aggregate_type, aggregate_id)
        state = {}
        for event in events:
            event_type = event["event_type"]
            event_data = event["event_data"]

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
            elif event_type == "UserRegistered":
                state = event_data.copy()
                state["id"] = aggregate_id
                state["is_active"] = True
            elif event_type == "UserUpdated":
                updated_fields = event_data.get("updated_fields", {})
                state.update(updated_fields)
        return state

    # שמירת Snapshot של המצב
    def save_snapshot(self, aggregate_type: str, aggregate_id: int, state: Dict[str, Any], version: int) -> int:
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

    # קבלת ה-Snapshot האחרון
    def get_latest_snapshot(self, aggregate_type: str, aggregate_id: int) -> Optional[Dict[str, Any]]:
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


# פונקציה שמחזירה מופע של EventStore
def get_event_store(db: Session) -> EventStore:
    return EventStore(db)
