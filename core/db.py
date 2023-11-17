from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings


POSTGRES_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_NAME}"

engine = create_engine(
    POSTGRES_URL, 
    #echo=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False, 
    autoflush=False, 
    expire_on_commit=False
    )

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()