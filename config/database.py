from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.setting import settings

engine = create_engine(settings.mssql_url)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()