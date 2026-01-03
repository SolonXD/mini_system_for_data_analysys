import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def make_engine():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    return create_engine(
        db_url,
        pool_pre_ping=True,
        future=True,
    )

ENGINE = make_engine()
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)
