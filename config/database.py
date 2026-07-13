from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.setting import settings

def create_database_engine(database_url: str, pool_recycle_seconds: int):
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=pool_recycle_seconds,
        pool_use_lifo=True,
    )


engine = create_database_engine(
    settings.mssql_url,
    settings.db_pool_recycle_seconds,
)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
