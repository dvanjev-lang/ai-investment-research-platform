from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), nullable=False, index=True)
    statement_type = Column(String(30), nullable=False)  # income | balance | cashflow
    period = Column(String(10), nullable=False)          # annual | quarterly
    fiscal_year = Column(Integer)
    fiscal_quarter = Column(Integer)
    period_end = Column(String(20))
    currency = Column(String(10), default="USD")

    # Income statement
    revenue = Column(Float)
    cost_of_revenue = Column(Float)
    gross_profit = Column(Float)
    operating_expenses = Column(Float)
    operating_income = Column(Float)
    ebitda = Column(Float)
    net_income = Column(Float)
    eps = Column(Float)
    eps_diluted = Column(Float)
    shares_outstanding = Column(Float)
    interest_expense = Column(Float)
    income_tax = Column(Float)
    depreciation_amortization = Column(Float)

    # Balance sheet
    cash = Column(Float)
    short_term_investments = Column(Float)
    total_current_assets = Column(Float)
    total_assets = Column(Float)
    total_current_liabilities = Column(Float)
    total_liabilities = Column(Float)
    total_equity = Column(Float)
    total_debt = Column(Float)
    net_debt = Column(Float)

    # Cash flow
    operating_cash_flow = Column(Float)
    capex = Column(Float)
    free_cash_flow = Column(Float)
    financing_cash_flow = Column(Float)
    investing_cash_flow = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
