from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    exchange = Column(String(50))
    sector = Column(String(100))
    industry = Column(String(150))
    description = Column(Text)
    headquarters = Column(String(255))
    employees = Column(Integer)
    website = Column(String(255))
    isin = Column(String(20))
    currency = Column(String(10), default="USD")
    extra_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
