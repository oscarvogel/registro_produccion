import logging
import ssl
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

def build_connect_args(
    database_url: str,
    *,
    mysql_ssl_ca: str = "",
    mysql_ssl_verify_cert: bool = True,
    mysql_ssl_verify_identity: bool = False,
) -> dict:
    """Build dialect-specific connection options without exposing credentials."""
    connect_args = {}
    if "sqlite" in database_url:
        connect_args["check_same_thread"] = False
    elif "mysql" in database_url or "pymysql" in database_url:
        from pymysql.converters import conversions
        from pymysql.constants import FIELD_TYPE
        import datetime

        custom_conv = conversions.copy()

        def convert_date(obj):
            """Convert MySQL date to Python date, treating invalid dates as None."""
            if obj is None or obj == b"0000-00-00":
                return None
            if isinstance(obj, bytes):
                obj = obj.decode("utf-8")
            if obj == "0000-00-00":
                return None
            try:
                return datetime.datetime.strptime(obj, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None

        custom_conv[FIELD_TYPE.DATE] = convert_date
        custom_conv[FIELD_TYPE.NEWDATE] = convert_date
        connect_args["conv"] = custom_conv
        connect_args["connect_timeout"] = 10
        connect_args["read_timeout"] = 30
        connect_args["write_timeout"] = 30
        if mysql_ssl_ca:
            connect_args["ssl"] = {
                "ca": mysql_ssl_ca,
                "check_hostname": mysql_ssl_verify_identity,
                "verify_mode": (
                    ssl.CERT_REQUIRED if mysql_ssl_verify_cert else ssl.CERT_NONE
                ),
            }
    return connect_args


connect_args = build_connect_args(
    settings.DATABASE_URL,
    mysql_ssl_ca=settings.MYSQL_SSL_CA,
    mysql_ssl_verify_cert=settings.MYSQL_SSL_VERIFY_CERT,
    mysql_ssl_verify_identity=settings.MYSQL_SSL_VERIFY_IDENTITY,
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
