from pydantic import BaseModel
from typing import Optional, List


class IncomeStatementRow(BaseModel):
    period: str
    fiscal_year: Optional[int] = None
    fiscal_quarter: Optional[int] = None
    revenue: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_expenses: Optional[float] = None
    operating_income: Optional[float] = None
    ebitda: Optional[float] = None
    depreciation_amortization: Optional[float] = None
    net_income: Optional[float] = None
    eps_diluted: Optional[float] = None
    shares_outstanding: Optional[float] = None


class BalanceSheetRow(BaseModel):
    period: str
    fiscal_year: Optional[int] = None
    cash: Optional[float] = None
    total_current_assets: Optional[float] = None
    total_assets: Optional[float] = None
    total_current_liabilities: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    total_debt: Optional[float] = None
    net_debt: Optional[float] = None


class CashFlowRow(BaseModel):
    period: str
    fiscal_year: Optional[int] = None
    operating_cash_flow: Optional[float] = None
    capex: Optional[float] = None
    free_cash_flow: Optional[float] = None
    financing_cash_flow: Optional[float] = None
    investing_cash_flow: Optional[float] = None


class FinancialRatios(BaseModel):
    ticker: str
    period: Optional[str] = None
    # Profitability
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    roa: Optional[float] = None
    roe: Optional[float] = None
    roic: Optional[float] = None
    # Liquidity
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    # Leverage
    debt_to_equity: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    interest_coverage: Optional[float] = None
    # Growth (YoY)
    revenue_growth: Optional[float] = None
    ebitda_growth: Optional[float] = None
    fcf_growth: Optional[float] = None


class FinancialsResponse(BaseModel):
    ticker: str
    period_type: str  # annual | quarterly
    income_statements: List[IncomeStatementRow] = []
    balance_sheets: List[BalanceSheetRow] = []
    cash_flows: List[CashFlowRow] = []
    ratios: List[FinancialRatios] = []
    currency: str = "USD"
    data_note: Optional[str] = None
