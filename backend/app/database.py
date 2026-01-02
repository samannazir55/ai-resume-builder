from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .core.config import settings

# Fix Render's postgres:// URL to postgresql://
database_url = settings.DATABASE_URL
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Conditional connect_args: only use check_same_thread for SQLite
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    echo=settings.DEBUG,  # Enable SQL query logging in debug mode
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency that provides a SQLAlchemy session for FastAPI routes.
    Properly closes the session after use and logs exceptions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()