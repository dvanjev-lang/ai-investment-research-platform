"""
Abstract base class for financial data providers.
Swap providers without changing application code.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.company import CompanyBase, CompanySearchResult, QuoteData, HistoricalPrice, PeerCompany
from app.schemas.financial import IncomeStatementRow, BalanceSheetRow, CashFlowRow, FinancialRatios


class FinancialDataProvider(ABC):

    @abstractmethod
    async def search_companies(self, query: str) -> List[CompanySearchResult]:
        ...

    @abstractmethod
    async def get_company(self, ticker: str) -> Optional[CompanyBase]:
        ...

    @abstractmethod
    async def get_quote(self, ticker: str) -> Optional[QuoteData]:
        ...

    @abstractmethod
    async def get_historical_prices(
        self, ticker: str, period: str = "1y"
    ) -> List[HistoricalPrice]:
        ...

    @abstractmethod
    async def get_income_statements(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> List[IncomeStatementRow]:
        ...

    @abstractmethod
    async def get_balance_sheets(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> List[BalanceSheetRow]:
        ...

    @abstractmethod
    async def get_cash_flows(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> List[CashFlowRow]:
        ...

    @abstractmethod
    async def get_financial_ratios(
        self, ticker: str, period: str = "annual", limit: int = 5
    ) -> List[FinancialRatios]:
        ...

    @abstractmethod
    async def get_peers(self, ticker: str) -> List[PeerCompany]:
        ...
