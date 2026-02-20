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

# Configure connect_args to handle invalid dates like '0000-00-00' by converting them to None
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False
elif "mysql" in settings.DATABASE_URL or "pymysql" in settings.DATABASE_URL:
    # PyMySQL-specific args to handle invalid dates
    from pymysql.converters import conversions
    from pymysql.constants import FIELD_TYPE
    import datetime
    
    # Create a custom conversion that turns '0000-00-00' into None
    custom_conv = conversions.copy()
    def convert_date(obj):
        """Convert MySQL date to Python date, treating invalid dates as None"""
        if obj is None or obj == b'0000-00-00':
            return None
        if isinstance(obj, bytes):
            obj = obj.decode('utf-8')
        if obj == '0000-00-00':
            return None
        try:
            return datetime.datetime.strptime(obj, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    
    custom_conv[FIELD_TYPE.DATE] = convert_date
    custom_conv[FIELD_TYPE.NEWDATE] = convert_date
    
    connect_args["conv"] = custom_conv

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
