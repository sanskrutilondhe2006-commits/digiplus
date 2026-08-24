from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, Float, Integer, String, Text, create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# --- DATABASE CONNECTION SETUP ---
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./logs.db")

connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- SQLALCHEMY MODEL ---
class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, index=True)
    severity = Column(String, index=True)
    source = Column(String, index=True)
    event = Column(String, index=True)
    score = Column(Float, default=0.0, index=True)
    message = Column(Text)
    reason = Column(Text)
    ai_analysis = Column(Text, nullable=True)


# --- DATABASE INITIALIZATION & DEPENDENCY ---
def init_db():
    """Creates tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- DATABASE INSERTION FUNCTION ---
def add_log_entry(
    db: Session,
    source: str,
    severity: str,
    event: str,
    score: float,
    message: str,
    reason: str,
    ai_analysis: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> LogEntry:
    """Creates, persists, and returns a new log entry record."""
    # Set UTC timestamp string if not explicitly provided
    if not timestamp:
        timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    db_log = LogEntry(
        timestamp=timestamp,
        severity=severity,
        source=source,
        event=event,
        score=score,
        message=message,
        reason=reason,
        ai_analysis=ai_analysis,
    )

    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        raise e


# --- DATABASE FETCHING FUNCTIONS ---
def fetch_logs(
    db: Session,
    search: Optional[str] = None,
    flagged_only: bool = False,
    anomaly_threshold: float = 0.7,
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    """Fetches log records with filtering, search, and pagination."""
    query = db.query(LogEntry)

    if flagged_only:
        query = query.filter(LogEntry.score >= anomaly_threshold)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                LogEntry.source.ilike(search_term),
                LogEntry.event.ilike(search_term),
                LogEntry.severity.ilike(search_term),
                LogEntry.message.ilike(search_term),
                LogEntry.reason.ilike(search_term),
            )
        )

    total_ingested = db.query(LogEntry).count()
    flagged_anomalies = (
        db.query(LogEntry).filter(LogEntry.score >= anomaly_threshold).count()
    )

    logs = query.order_by(LogEntry.id.desc()).offset(offset).limit(limit).all()

    return {
        "total_ingested": total_ingested,
        "flagged_anomalies": flagged_anomalies,
        "returned_count": len(logs),
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "severity": log.severity,
                "source": log.source,
                "event": log.event,
                "score": log.score,
                "message": log.message,
                "reason": log.reason,
                "ai_analysis": log.ai_analysis,
            }
            for log in logs
        ],
    }


def fetch_log_by_id(db: Session, log_id: int) -> Optional[LogEntry]:
    """Fetches a single log record by its Primary Key ID."""
    return db.query(LogEntry).filter(LogEntry.id == log_id).first()