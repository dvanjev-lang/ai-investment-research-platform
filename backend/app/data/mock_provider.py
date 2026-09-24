"""
Mock data provider — returns realistic demo data for development and portfolio demos.
All values are illustrative. Clearly labeled as demo data.
"""

import random
from datetime import date, timedelta
from typing import List, Optional

from app.data.base import FinancialDataProvider
from app.schemas.company import CompanyBase, CompanySearchResult, QuoteData, HistoricalPrice, PeerCompany
from app.schemas.financial import IncomeStatementRow, BalanceSheetRow, CashFlowRow, FinancialRatios

DEMO_NOTE = "DEMO DATA — Illustrative only. Not sourced from live financial data feeds."

MOCK_COMPANIES = {
    "NVDA": {
        "name": "NVIDIA Corporation",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "industry": "Semiconductors",
        "description": "NVIDIA Corporation designs and manufactures graphics processing units (GPUs) and system-on-chip units. The company operates through two segments: Graphics and Compute & Networking.",
        "headquarters": "Santa Clara, California, USA",
        "employees": 29600,
        "website": "https://www.nvidia.com",
        "currency": "USD",
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "industry": "Software—Infrastructure",
        "description": "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.",
        "headquarters": "Redmond, Washington, USA",
        "employees": 221000,
        "website": "https://www.microsoft.com",
        "currency": "USD",
    },
    "AAPL": {
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.",
        "headquarters": "Cupertino, California, USA",
        "employees": 164000,
        "website": "https://www.apple.com",
        "currency": "USD",
    },
    "AMZN": {
        "name": "Amazon.com, Inc.",
        "exchange": "NASDAQ",
        "sector": "Consumer Cyclical",
        "industry": "Internet Retail",
        "description": "Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions through online and physical stores in North America and internationally.",
        "headquarters": "Seattle, Washington, USA",
        "employees": 1525000,
        "website": "https://www.amazon.com",
        "currency": "USD",
    },
    "JPM": {
        "name": "JPMorgan Chase & Co.",
        "exchange": "NYSE",
        "sector": "Financial Services",
        "industry": "Banks—Diversified",
        "description": "JPMorgan Chase & Co. is a financial holding company. It provides investment banking, financial services for consumers and small businesses, commercial banking, financial transaction processing, and asset management.",
        "headquarters": "New York, New York, USA",
        "employees": 309926,
        "website": "https://www.jpmorganchase.com",
        "currency": "USD",
    },
    "ASML": {
        "name": "ASML Holding N.V.",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "industry": "Semiconductor Equipment",
        "description": "ASML Holding N.V. develops, produces, markets, sells, and services advanced semiconductor equipment systems.",
        "headquarters": "Veldhoven, Netherlands",
        "employees": 42000,
        "website": "https://www.asml.com",
        "currency": "EUR",
    },
    "BLK": {
        "name": "BlackRock, Inc.",
        "exchange": "NYSE",
        "sector": "Financial Services",
        "industry": "Asset Management",
        "description": "BlackRock, Inc. is a publicly owned investment manager. It provides investment management, risk management, and advisory services.",
        "headquarters": "New York, New York, USA",
        "employees": 21000,
        "website": "https://www.blackrock.com",
        "currency": "USD",
    },
    "AMD": {
        "name": "Advanced Micro Devices, Inc.",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "industry": "Semiconductors",
        "description": "Advanced Micro Devices, Inc. operates as a semiconductor company worldwide. It operates through Data Center, Client, Gaming, and Embedded segments.",
        "headquarters": "Santa Clara, California, USA",
        "employees": 26000,
        "website": "https://www.amd.com",
        "currency": "USD",
    },
}

MOCK_QUOTES = {
    "NVDA": {"price": 875.40, "change": 12.50, "change_pct": 1.45, "market_cap": 2.16e12, "high_52w": 974.00, "low_52w": 402.23, "pe_ratio": 68.2, "forward_pe": 38.5, "ev_ebitda": 52.1, "beta": 1.68, "dividend_yield": 0.0, "price_to_book": 42.1},
    "MSFT": {"price": 415.32, "change": 2.18, "change_pct": 0.53, "market_cap": 3.09e12, "high_52w": 468.35, "low_52w": 309.45, "pe_ratio": 35.8, "forward_pe": 30.2, "ev_ebitda": 27.4, "beta": 0.90, "dividend_yield": 0.0072, "price_to_book": 12.6},
    "AAPL": {"price": 191.24, "change": -1.32, "change_pct": -0.68, "market_cap": 2.95e12, "high_52w": 220.20, "low_52w": 164.08, "pe_ratio": 30.5, "forward_pe": 27.8, "ev_ebitda": 21.3, "beta": 1.25, "dividend_yield": 0.0053, "price_to_book": 44.2},
    "AMZN": {"price": 195.80, "change": 3.45, "change_pct": 1.79, "market_cap": 2.05e12, "high_52w": 201.20, "low_52w": 118.35, "pe_ratio": 58.3, "forward_pe": 38.1, "ev_ebitda": 20.5, "beta": 1.35, "dividend_yield": 0.0, "price_to_book": 8.5},
    "JPM": {"price": 210.45, "change": 0.95, "change_pct": 0.45, "market_cap": 6.08e11, "high_52w": 220.82, "low_52w": 135.19, "pe_ratio": 12.3, "forward_pe": 11.8, "ev_ebitda": None, "beta": 1.10, "dividend_yield": 0.024, "price_to_book": 1.9},
    "ASML": {"price": 875.20, "change": -5.30, "change_pct": -0.60, "market_cap": 3.45e11, "high_52w": 1110.09, "low_52w": 622.50, "pe_ratio": 40.2, "forward_pe": 30.5, "ev_ebitda": 26.8, "beta": 1.42, "dividend_yield": 0.008, "price_to_book": 18.5},
    "BLK": {"price": 918.35, "change": 4.20, "change_pct": 0.46, "market_cap": 1.38e11, "high_52w": 1028.22, "low_52w": 671.20, "pe_ratio": 22.5, "forward_pe": 19.8, "ev_ebitda": 14.2, "beta": 1.35, "dividend_yield": 0.025, "price_to_book": 3.4},
    "AMD": {"price": 156.75, "change": 2.85, "change_pct": 1.85, "market_cap": 2.53e11, "high_52w": 227.30, "low_52w": 95.83, "pe_ratio": 198.4, "forward_pe": 32.1, "ev_ebitda": 42.3, "beta": 1.72, "dividend_yield": 0.0, "price_to_book": 3.8},
}

# Income statement data (in millions USD) — 5 years annual
MOCK_INCOME = {
    "NVDA": [
        {"fiscal_year": 2024, "revenue": 60922, "gross_profit": 44301, "operating_income": 32972, "ebitda": 34000, "net_income": 29760, "eps_diluted": 11.93, "shares_outstanding": 2490, "interest_expense": 67, "depreciation_amortization": 1028},
        {"fiscal_year": 2023, "revenue": 26974, "gross_profit": 15356, "operating_income": 4224, "ebitda": 5252, "net_income": 4368, "eps_diluted": 1.74, "shares_outstanding": 2508, "interest_expense": 262, "depreciation_amortization": 1028},
        {"fiscal_year": 2022, "revenue": 26914, "gross_profit": 17475, "operating_income": 10041, "ebitda": 11069, "net_income": 9752, "eps_diluted": 3.85, "shares_outstanding": 2533, "interest_expense": 236, "depreciation_amortization": 1028},
        {"fiscal_year": 2021, "revenue": 16675, "gross_profit": 10203, "operating_income": 4532, "ebitda": 5346, "net_income": 4332, "eps_diluted": 1.73, "shares_outstanding": 2507, "interest_expense": 184, "depreciation_amortization": 814},
        {"fiscal_year": 2020, "revenue": 10918, "gross_profit": 6347, "operating_income": 2846, "ebitda": 3330, "net_income": 2796, "eps_diluted": 1.13, "shares_outstanding": 2476, "interest_expense": 52, "depreciation_amortization": 484},
    ],
    "MSFT": [
        {"fiscal_year": 2024, "revenue": 245122, "gross_profit": 169274, "operating_income": 109433, "ebitda": 134000, "net_income": 88136, "eps_diluted": 11.80, "shares_outstanding": 7468, "interest_expense": 2063, "depreciation_amortization": 25000},
        {"fiscal_year": 2023, "revenue": 211915, "gross_profit": 146052, "operating_income": 88523, "ebitda": 110000, "net_income": 72361, "eps_diluted": 9.65, "shares_outstanding": 7496, "interest_expense": 1874, "depreciation_amortization": 22000},
        {"fiscal_year": 2022, "revenue": 198270, "gross_profit": 135620, "operating_income": 83383, "ebitda": 100000, "net_income": 72738, "eps_diluted": 9.65, "shares_outstanding": 7540, "interest_expense": 1575, "depreciation_amortization": 17000},
        {"fiscal_year": 2021, "revenue": 168088, "gross_profit": 115856, "operating_income": 69916, "ebitda": 85000, "net_income": 61271, "eps_diluted": 8.05, "shares_outstanding": 7608, "interest_expense": 1373, "depreciation_amortization": 15000},
        {"fiscal_year": 2020, "revenue": 143015, "gross_profit": 96937, "operating_income": 52959, "ebitda": 65000, "net_income": 44281, "eps_diluted": 5.76, "shares_outstanding": 7683, "interest_expense": 1462, "depreciation_amortization": 12000},
    ],
}

# Balance sheets (in millions USD)
MOCK_BALANCE = {
    "NVDA": [
        {"fiscal_year": 2024, "cash": 31442, "total_current_assets": 44345, "total_assets": 65728, "total_current_liabilities": 10631, "total_liabilities": 22892, "total_equity": 42978, "total_debt": 8461, "net_debt": -22981},
        {"fiscal_year": 2023, "cash": 13296, "total_current_assets": 23073, "total_assets": 41193, "total_current_liabilities": 6983, "total_liabilities": 17575, "total_equity": 22101, "total_debt": 9703, "net_debt": -3593},
        {"fiscal_year": 2022, "cash": 19473, "total_current_assets": 28829, "total_assets": 44187, "total_current_liabilities": 5978, "total_liabilities": 17575, "total_equity": 26612, "total_debt": 9703, "net_debt": -9770},
    ],
    "MSFT": [
        {"fiscal_year": 2024, "cash": 75523, "total_current_assets": 159734, "total_assets": 512163, "total_current_liabilities": 125286, "total_liabilities": 243686, "total_equity": 268477, "total_debt": 79399, "net_debt": 3876},
        {"fiscal_year": 2023, "cash": 111262, "total_current_assets": 184257, "total_assets": 411976, "total_current_liabilities": 104149, "total_liabilities": 205753, "total_equity": 206223, "total_debt": 59858, "net_debt": -51404},
    ],
}

MOCK_CASHFLOW = {
    "NVDA": [
        {"fiscal_year": 2024, "operating_cash_flow": 28090, "capex": -2833, "free_cash_flow": 27257, "financing_cash_flow": -10648, "investing_cash_flow": -10575},
        {"fiscal_year": 2023, "operating_cash_flow": 5641, "capex": -1833, "free_cash_flow": 3808, "financing_cash_flow": -10648, "investing_cash_flow": -9500},
        {"fiscal_year": 2022, "operating_cash_flow": 9108, "capex": -976, "free_cash_flow": 8132, "financing_cash_flow": -12987, "investing_cash_flow": -10000},
    ],
    "MSFT": [
        {"fiscal_year": 2024, "operating_cash_flow": 118547, "capex": -44482, "free_cash_flow": 74065, "financing_cash_flow": -37195, "investing_cash_flow": -79442},
        {"fiscal_year": 2023, "operating_cash_flow": 87582, "capex": -28107, "free_cash_flow": 59475, "financing_cash_flow": -43000, "investing_cash_flow": -60000},
    ],
}

MOCK_PEERS = {
    "NVDA": ["AMD", "INTC", "QCOM", "AVGO", "AMAT"],
    "MSFT": ["AAPL", "GOOGL", "META", "AMZN", "ORCL"],
    "AAPL": ["MSFT", "GOOGL", "META", "SAMSUNG"],
    "JPM": ["BAC", "GS", "MS", "C", "WFC"],
    "ASML": ["AMAT", "LRCX", "KLAC"],
    "AMD": ["NVDA", "INTC", "QCOM"],
}


def _get_fallback_company(ticker: str) -> dict:
    return {
        "name": f"{ticker} Corporation",
        "exchange": "NYSE",
        "sector": "Technology",
        "industry": "General",
        "description": f"Demo company data for {ticker}. Live data unavailable.",
        "headquarters": "United States",
        "employees": None,
        "website": None,
        "currency": "USD",
    }


class MockDataProvider(FinancialDataProvider):
    """Returns static demo data. Clearly labeled as illustrative."""

    async def search_companies(self, query: str) -> List[CompanySearchResult]:
        query_lower = query.lower()
        results = []
        for ticker, data in MOCK_COMPANIES.items():
            if (
                query_lower in ticker.lower()
                or query_lower in data["name"].lower()
                or query_lower in data.get("sector", "").lower()
            ):
                results.append(CompanySearchResult(
                    ticker=ticker,
                    name=data["name"],
                    exchange=data["exchange"],
                    sector=data["sector"],
                    industry=data["industry"],
                    currency=data["currency"],
                ))
        return results

    async def get_company(self, ticker: str) -> Optional[CompanyBase]:
        ticker = ticker.upper()
        data = MOCK_COMPANIES.get(ticker, _get_fallback_company(ticker))
        return CompanyBase(ticker=ticker, **data)

    async def get_quote(self, ticker: str) -> Optional[QuoteData]:
        ticker = ticker.upper()
        raw = MOCK_QUOTES.get(ticker)
        if not raw:
            return QuoteData(
                ticker=ticker,
                price=100.0,
                data_note=DEMO_NOTE,
            )
        return QuoteData(
            ticker=ticker,
            **raw,
            fetched_at="2024-10-01",
            data_note=DEMO_NOTE,
        )

    async def get_historical_prices(
        self, ticker: str, period: str = "1y"
    ) -> List[HistoricalPrice]:
        ticker = ticker.upper()
        quote = MOCK_QUOTES.get(ticker, {})
        base_price = quote.get("price", 100.0)

        days = {"1m": 30, "3m": 90, "6m": 180, "1y": 252, "3y": 756, "5y": 1260}.get(period, 252)
        prices = []
        price = base_price * 0.70
        today = date.today()

        random.seed(hash(ticker))
        for i in range(days, 0, -1):
            d = today - timedelta(days=i)
            if d.weekday() >= 5:
                continue
            change_pct = random.gauss(0.0005, 0.015)
            price = price * (1 + change_pct)
            prices.append(HistoricalPrice(
                date=d.isoformat(),
                open=round(price * 0.999, 2),
                high=round(price * 1.012, 2),
                low=round(price * 0.988, 2),
                close=round(price, 2),
                adjusted_close=round(price, 2),
                volume=round(random.uniform(10e6, 80e6)),
            ))
        return prices

    async def get_income_statements(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> List[IncomeStatementRow]:
        ticker = ticker.upper()
        raw = MOCK_INCOME.get(ticker, [])
        results = []
        for row in raw[:limit]:
            cost = row["revenue"] - row["gross_profit"]
            op_ex = row["gross_profit"] - row["operating_income"]
            results.append(IncomeStatementRow(
                period=period,
                fiscal_year=row["fiscal_year"],
                revenue=row["revenue"],
                cost_of_revenue=cost,
                gross_profit=row["gross_profit"],
                operating_expenses=op_ex,
                operating_income=row["operating_income"],
                ebitda=row["ebitda"],
                net_income=row["net_income"],
                eps_diluted=row["eps_diluted"],
                shares_outstanding=row["shares_outstanding"],
            ))
        return results

    async def get_balance_sheets(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> List[BalanceSheetRow]:
        ticker = ticker.upper()
        raw = MOCK_BALANCE.get(ticker, [])
        return [BalanceSheetRow(period=period, **row) for row in raw[:limit]]

    async def get_cash_flows(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> List[CashFlowRow]:
        ticker = ticker.upper()
        raw = MOCK_CASHFLOW.get(ticker, [])
        return [CashFlowRow(period=period, **row) for row in raw[:limit]]

    async def get_financial_ratios(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> List[FinancialRatios]:
        ticker = ticker.upper()
        income = await self.get_income_statements(ticker, period, limit)
        balance = await self.get_balance_sheets(ticker, period, limit)
        cashflow = await self.get_cash_flows(ticker, period, limit)
        ratios = []
        for i, inc in enumerate(income):
            bal = balance[i] if i < len(balance) else None
            cf = cashflow[i] if i < len(cashflow) else None
            gm = (inc.gross_profit / inc.revenue) if inc.revenue else None
            om = (inc.operating_income / inc.revenue) if inc.revenue else None
            nm = (inc.net_income / inc.revenue) if inc.revenue else None
            em = (inc.ebitda / inc.revenue) if inc.revenue and inc.ebitda else None
            roa = (inc.net_income / bal.total_assets) if bal and bal.total_assets else None
            roe = (inc.net_income / bal.total_equity) if bal and bal.total_equity else None
            dte = (bal.total_debt / bal.total_equity) if bal and bal.total_equity and bal.total_debt else None
            dteb = (bal.total_debt / inc.ebitda) if inc.ebitda and bal and bal.total_debt else None
            cr = (bal.total_current_assets / bal.total_current_liabilities) if bal and bal.total_current_liabilities else None
            fcf_m = (cf.free_cash_flow / inc.revenue) if cf and inc.revenue else None
            # YoY growth
            rev_g = None
            if i + 1 < len(income) and income[i + 1].revenue:
                rev_g = (inc.revenue - income[i + 1].revenue) / income[i + 1].revenue
            ratios.append(FinancialRatios(
                ticker=ticker,
                period=str(inc.fiscal_year),
                gross_margin=gm,
                operating_margin=om,
                net_margin=nm,
                ebitda_margin=em,
                roa=roa,
                roe=roe,
                debt_to_equity=dte,
                debt_to_ebitda=dteb,
                current_ratio=cr,
                revenue_growth=rev_g,
            ))
        return ratios

    async def get_peers(self, ticker: str) -> List[PeerCompany]:
        ticker = ticker.upper()
        peer_tickers = MOCK_PEERS.get(ticker, [])
        peers = []
        for pt in peer_tickers:
            pdata = MOCK_COMPANIES.get(pt, {})
            quote = MOCK_QUOTES.get(pt, {})
            peers.append(PeerCompany(
                ticker=pt,
                name=pdata.get("name", pt),
                market_cap=quote.get("market_cap"),
                pe_ratio=quote.get("pe_ratio"),
                ev_ebitda=quote.get("ev_ebitda"),
            ))
        return peers
