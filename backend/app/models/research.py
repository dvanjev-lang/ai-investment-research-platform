from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class ResearchQuery(Base):
    __tablename__ = "research_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    citations = Column(JSON)    # list of citation objects
    agent_trace = Column(JSON)  # which agents ran, what they found
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    latency_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), index=True)
    title = Column(String(500))
    content = Column(JSON)      # structured sections
    data_through = Column(String(50))
    sources = Column(JSON)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    model_used = Column(String(100))
