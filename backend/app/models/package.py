from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)       # e.g. "Student Pack"
    price = Column(Float)                   # e.g. 5.00
    credits = Column(Integer)               # e.g. 10
    description = Column(String)            
    payment_link = Column(String)           # Gumroad/Stripe/SadaBiz URL
    badge = Column(String, nullable=True)   # "POPULAR"
    is_active = Column(Boolean, default=True)
