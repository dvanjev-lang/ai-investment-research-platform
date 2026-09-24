from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class Citation(BaseModel):
    source_type: str          # document | financial_data | market_data
    source_name: str
    document_id: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    excerpt: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None


class AgentStep(BaseModel):
    agent: str
    action: str
    result_summary: str
    sources_consulted: List[str] = []


class ResearchQueryRequest(BaseModel):
    ticker: str
    question: str
    include_documents: bool = True
    include_financial_data: bool = True


class ResearchQueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation] = []
    agent_trace: List[AgentStep] = []
    data_through: Optional[str] = None
    disclaimer: str = (
        "This analysis is for informational purposes only and does not constitute "
        "investment advice or a recommendation to buy or sell any security."
    )
    confidence_note: Optional[str] = None


class ReportSection(BaseModel):
    title: str
    content: str
    subsections: Optional[List["ReportSection"]] = None
    citations: List[Citation] = []


class ReportRequest(BaseModel):
    ticker: str
    include_dcf: bool = False
    include_peers: bool = True


class ReportResponse(BaseModel):
    ticker: str
    company_name: str
    title: str
    generated_at: str
    data_through: str
    sections: List[ReportSection]
    sources: List[Citation]
    disclaimer: str = (
        "This report is generated for informational and educational purposes only. "
        "It does not constitute investment advice. All financial data is sourced from "
        "publicly available information and should be independently verified."
    )
