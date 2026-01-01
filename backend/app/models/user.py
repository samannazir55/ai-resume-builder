from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)

    subscription_plan = Column(String, default="free")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
