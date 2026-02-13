import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Ensure PyMySQL is available as MySQLdb for libraries expecting the MySQLdb API
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    logging.debug("PyMySQL not available to install_as_MySQLdb; ensure pymysql is installed if using pymysql driver")

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
