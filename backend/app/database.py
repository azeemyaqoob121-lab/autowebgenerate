"""Database Connection and Session Management with Enhanced Monitoring"""
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import Pool
import logging
from typing import Generator

from .config import settings

# Module logger
logger = logging.getLogger(__name__)

# Create database engine with connection pooling configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Maximum number of permanent connections
    max_overflow=10,  # Maximum number of connections beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=settings.DEBUG,  # Log all SQL statements in debug mode
    echo_pool=False,  # Set to True to debug connection pool issues
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# Connection pool event listeners for monitoring
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when a new connection is created"""
    logger.debug("Database connection established")


@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool"""
    logger.debug("Database connection checked out from pool")


@event.listens_for(Pool, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log when a connection is returned to the pool"""
    logger.debug("Database connection returned to pool")


# Slow query logging
import time

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Record query start time"""
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries (> 1 second)"""
    total = time.time() - conn.info['query_start_time'].pop(-1)

    # Log queries taking longer than 1 second
    if total > 1.0:
        logger.warning(
            f"Slow query detected ({total:.2f}s): {statement}",
            extra={
                'execution_time': total,
                'statement': statement,
                'parameters': parameters
            }
        )
    # In debug mode, log all queries with execution time
    elif settings.DEBUG and total > 0.1:  # Log queries > 100ms in debug mode
        logger.debug(
            f"Query executed in {total:.2f}s: {statement[:100]}...",
            extra={'execution_time': total}
        )


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI route handlers.

    Provides a SQLAlchemy session with automatic lifecycle management:
    - Creates a new session for each request
    - Ensures session is properly closed after request completion
    - Handles exceptions gracefully with automatic rollback

    Usage in FastAPI routes:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            # Use db session here
            pass

    Yields:
        Session: SQLAlchemy database session

    Example:
        ```python
        from fastapi import Depends
        from sqlalchemy.orm import Session
        from app.database import get_db

        @app.get("/businesses")
        def get_businesses(db: Session = Depends(get_db)):
            businesses = db.query(Business).all()
            return businesses
        ```
    """
    db = SessionLocal()
    logger.debug("Database session created")
    try:
        yield db
        logger.debug("Database session completed successfully")
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


def get_pool_status() -> dict:
    """
    Get current database connection pool status for monitoring.

    Returns:
        dict: Connection pool statistics including:
            - pool_size: Maximum number of permanent connections
            - checked_out: Number of connections currently in use
            - overflow: Number of connections beyond pool_size
            - total: Total number of connections (checked_out + overflow)

    Example:
        ```python
        status = get_pool_status()
        print(f"Active connections: {status['checked_out']}/{status['pool_size']}")
        ```
    """
    pool_status = {
        "pool_size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "total": engine.pool.checkedout() + engine.pool.overflow()
    }
    return pool_status
