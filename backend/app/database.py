from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Enable SQL query logging in debug mode
    connect_args={"check_same_thread": False},
    # pool_size only relevant for certain RDBMS, not SQLite
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
