from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), nullable=False, index=True)
    name = Column(String(500))
    document_type = Column(String(50))   # annual_report | quarterly_report | presentation
    reporting_period = Column(String(20))
    publication_date = Column(String(20))
    source_url = Column(String(1000))
    file_path = Column(String(1000))
    page_count = Column(Integer)
    word_count = Column(Integer)
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    ticker = Column(String(20), index=True)
    chunk_index = Column(Integer)
    content = Column(Text, nullable=False)
    page_number = Column(Integer)
    section = Column(String(255))
    embedding = Column(JSON)    # stored as list; use pgvector in prod
    token_count = Column(Integer)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
