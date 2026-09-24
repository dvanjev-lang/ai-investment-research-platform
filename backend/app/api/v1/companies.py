from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime

from app.data.provider_factory import get_data_provider
from app.schemas.company import CompanyProfile, CompanySearchResult
from app.schemas.financial import FinancialsResponse

router = APIRouter()


@router.get("/search", response_model=list[CompanySearchResult])
async def search_companies(q: str = Query(..., min_length=1)):
    provider = get_data_provider()
    results = await provider.search_companies(q)
    return results


@router.get("/{ticker}", response_model=CompanyProfile)
async def get_company(ticker: str):
    provider = get_data_provider()
    company = await provider.get_company(ticker.upper())
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")
    quote = await provider.get_quote(ticker.upper())
    return CompanyProfile(
        company=company,
        quote=quote,
        data_as_of=datetime.utcnow().strftime("%Y-%m-%d"),
        data_provider="mock (demo)",
    )


@router.get("/{ticker}/prices")
async def get_historical_prices(ticker: str, period: str = "1y"):
    provider = get_data_provider()
    prices = await provider.get_historical_prices(ticker.upper(), period)
    return {"ticker": ticker.upper(), "period": period, "data": prices}


@router.get("/{ticker}/financials", response_model=FinancialsResponse)
async def get_financials(ticker: str, period: str = "annual"):
    provider = get_data_provider()
    ticker = ticker.upper()
    income = await provider.get_income_statements(ticker, period)
    balance = await provider.get_balance_sheets(ticker, period)
    cashflow = await provider.get_cash_flows(ticker, period)
    ratios = await provider.get_financial_ratios(ticker, period)
    return FinancialsResponse(
        ticker=ticker,
        period_type=period,
        income_statements=income,
        balance_sheets=balance,
        cash_flows=cashflow,
        ratios=ratios,
        data_note="DEMO DATA — Illustrative only.",
    )


@router.get("/{ticker}/peers")
async def get_peers(ticker: str):
    provider = get_data_provider()
    peers = await provider.get_peers(ticker.upper())
    return {"ticker": ticker.upper(), "peers": peers}
