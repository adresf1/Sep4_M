from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

_engine = None
_SessionLocal = None

def get_database_url():
    return os.getenv("DATABASE_URL", "postgresql://dummy_url")

def get_engine():
    global _engine
    if _engine is None:
        db_url = get_database_url()
        _engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=2,
            pool_recycle=1800,
            pool_pre_ping=True
        )
    return _engine

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal

def SessionLocal():
    return get_session_local()()