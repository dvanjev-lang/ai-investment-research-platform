from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), nullable=False, index=True)
    price = Column(Float)
    change = Column(Float)
    change_pct = Column(Float)
    market_cap = Column(Float)
    volume = Column(Float)
    avg_volume = Column(Float)
    high_52w = Column(Float)
    low_52w = Column(Float)
    pe_ratio = Column(Float)
    forward_pe = Column(Float)
    ev_ebitda = Column(Float)
    price_to_book = Column(Float)
    dividend_yield = Column(Float)
    beta = Column(Float)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
