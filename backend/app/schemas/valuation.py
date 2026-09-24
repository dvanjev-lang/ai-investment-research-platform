from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class DCFAssumptions(BaseModel):
    revenue_growth_rates: List[float] = Field(
        default=[0.15, 0.12, 0.10, 0.08, 0.06],
        description="Year-by-year revenue growth rates (5 years)"
    )
    ebitda_margin: float = Field(default=0.25, description="Assumed EBITDA margin")
    tax_rate: float = Field(default=0.21, description="Effective tax rate")
    capex_pct_revenue: float = Field(default=0.05, description="CapEx as % of revenue")
    nwc_change_pct_revenue: float = Field(default=0.02, description="Change in NWC as % of revenue")
    wacc: float = Field(default=0.10, description="Weighted Average Cost of Capital")
    terminal_growth_rate: float = Field(default=0.025, description="Terminal growth rate")
    base_revenue: float = Field(description="Base year revenue in millions USD")


class DCFScenario(BaseModel):
    name: str
    assumptions: DCFAssumptions
    projected_revenues: List[float] = []
    projected_fcf: List[float] = []
    terminal_value: Optional[float] = None
    enterprise_value: Optional[float] = None
    equity_value: Optional[float] = None
    implied_price: Optional[float] = None
    shares_outstanding: Optional[float] = None


class SensitivityMatrix(BaseModel):
    row_label: str       # e.g. "WACC"
    col_label: str       # e.g. "Terminal Growth Rate"
    row_values: List[float]
    col_values: List[float]
    matrix: List[List[float]]   # implied price at each combination


class DCFResponse(BaseModel):
    ticker: str
    base_case: DCFScenario
    conservative_case: DCFScenario
    optimistic_case: DCFScenario
    sensitivity: SensitivityMatrix
    methodology_note: str = (
        "DCF analysis is based on user-selected assumptions and is purely illustrative. "
        "It does not represent a target price, fair value, or investment recommendation. "
        "Small changes in assumptions can materially affect implied valuations."
    )
    generated_at: Optional[str] = None
