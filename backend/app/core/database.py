import os
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
from app.core.logging import logger

DATABASE_URL = settings.DATABASE_URL
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQLITE_FALLBACK_FILE = os.path.join(BACKEND_DIR, "jobguard.db").replace("\\", "/")

def test_mysql_connection(url: str) -> bool:
    """Check if MySQL server is reachable."""
    try:
        import pymysql
        clean_url = url.replace("mysql+pymysql://", "mysql://")
        parsed = urlparse(clean_url)
        db_name = parsed.path.lstrip("/").split("?")[0]
        user = parsed.username or "root"
        password = parsed.password or ""
        host = parsed.hostname or "localhost"
        port = parsed.port or 3306

        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            charset="utf8mb4",
            connect_timeout=2
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        logger.info(f"MySQL connection established. Database '{db_name}' ready.")
        return True
    except Exception as e:
        logger.warning(
            f"MySQL connection could not be established ({e}). "
            "Using local SQLite fallback so JobGuard AI runs with zero interruptions."
        )
        return False

# Smart engine initialization with graceful fallback
active_url = DATABASE_URL
engine_kwargs = {"pool_pre_ping": True}

if DATABASE_URL.startswith("mysql"):
    if test_mysql_connection(DATABASE_URL):
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_recycle"] = 3600
        active_url = DATABASE_URL
    else:
        active_url = f"sqlite:///{SQLITE_FALLBACK_FILE}"
        engine_kwargs["connect_args"] = {"check_same_thread": False}
elif DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(active_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
