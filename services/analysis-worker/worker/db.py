from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from worker.config import get_settings

_settings = get_settings()

# Celery tasks are sync — use synchronous psycopg2 driver here.
_sync_url = _settings.database_url.replace("+asyncpg", "")
_engine = create_engine(_sync_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
_Session = sessionmaker(bind=_engine, class_=Session, expire_on_commit=False)


@contextmanager
def db_session():
    s = _Session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
