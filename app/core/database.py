from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    pass
