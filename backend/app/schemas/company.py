from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CompanyBase(BaseModel):
    ticker: str
    name: str
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    headquarters: Optional[str] = None
    employees: Optional[int] = None
    website: Optional[str] = None
    currency: Optional[str] = "USD"


class CompanySearchResult(BaseModel):
    ticker: str
    name: str
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    currency: Optional[str] = None


class QuoteData(BaseModel):
    ticker: str
    price: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    ev_ebitda: Optional[float] = None
    price_to_book: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    fetched_at: Optional[str] = None
    data_note: Optional[str] = None


class HistoricalPrice(BaseModel):
    date: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    adjusted_close: Optional[float] = None
    volume: Optional[float] = None


class CompanyProfile(BaseModel):
    company: CompanyBase
    quote: Optional[QuoteData] = None
    data_as_of: Optional[str] = None
    data_provider: str = "mock"
    disclaimer: str = (
        "This platform provides informational and analytical content for educational "
        "and research purposes only. It does not constitute investment advice."
    )


class PeerCompany(BaseModel):
    ticker: str
    name: str
    market_cap: Optional[float] = None
    revenue: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    pe_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    revenue_growth: Optional[float] = None
    roic: Optional[float] = None
