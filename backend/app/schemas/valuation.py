from pydantic import BaseModel, Field, model_validator
from typing import Optional, List


class DCFAssumptions(BaseModel):
    """
    Assumptions for a 5-year DCF model using EBIT-based NOPAT.

    FCF = NOPAT - CapEx - ΔNWC
    NOPAT = EBIT × (1 - tax_rate)
    EBIT = EBITDA - D&A
    Terminal Value = FCF_n × (1 + g) / (WACC - g)   [Gordon Growth]
    """
    revenue_growth_rates: List[float] = Field(
        default=[0.15, 0.12, 0.10, 0.08, 0.06],
        description="Year-by-year revenue growth rates for forecast period (5 values)"
    )
    ebitda_margin: float = Field(
        default=0.25,
        ge=0.0, le=1.0,
        description="EBITDA as a fraction of revenue (e.g. 0.25 = 25%)"
    )
    da_pct_revenue: float = Field(
        default=0.04,
        ge=0.0, le=0.5,
        description="Depreciation & Amortisation as a fraction of revenue. EBIT = EBITDA - D&A."
    )
    tax_rate: float = Field(
        default=0.21,
        ge=0.0, le=0.99,
        description="Effective corporate tax rate"
    )
    capex_pct_revenue: float = Field(
        default=0.05,
        ge=0.0, le=1.0,
        description="Capital expenditures as a fraction of revenue"
    )
    nwc_change_pct_revenue: float = Field(
        default=0.02,
        ge=-0.5, le=0.5,
        description="Change in net working capital as a fraction of revenue (positive = cash use)"
    )
    wacc: float = Field(
        default=0.10,
        ge=0.01, le=0.50,
        description="Weighted Average Cost of Capital"
    )
    terminal_growth_rate: float = Field(
        default=0.025,
        ge=0.0, le=0.10,
        description="Perpetuity growth rate for terminal value (Gordon Growth)"
    )
    base_revenue: float = Field(
        description="Most recent full-year revenue in millions (same currency as model output)",
        gt=0.0
    )

    @model_validator(mode='after')
    def validate_wacc_exceeds_terminal_growth(self) -> 'DCFAssumptions':
        spread = self.wacc - self.terminal_growth_rate
        if spread <= 0:
            raise ValueError(
                f"WACC ({self.wacc:.1%}) must exceed terminal growth rate "
                f"({self.terminal_growth_rate:.1%}). "
                f"The Gordon Growth terminal value formula requires WACC > g."
            )
        if spread < 0.01:
            raise ValueError(
                f"WACC-TGR spread is only {spread:.1%}. "
                f"A spread below 1% produces unreliable terminal values. "
                f"Increase WACC or decrease terminal growth rate."
            )
        if self.da_pct_revenue >= self.ebitda_margin:
            raise ValueError(
                f"D&A ({self.da_pct_revenue:.1%} of revenue) >= EBITDA margin "
                f"({self.ebitda_margin:.1%}). This would produce negative EBIT. "
                f"Review your margin assumptions."
            )
        return self


class DCFYearProjection(BaseModel):
    """Single-year projection output for transparency."""
    year: int
    revenue: float
    ebitda: float
    da: float
    ebit: float
    nopat: float
    capex: float
    delta_nwc: float
    free_cash_flow: float
    pv_fcf: float


class DCFScenario(BaseModel):
    name: str
    assumptions: DCFAssumptions
    projections: List[DCFYearProjection] = []
    terminal_value: Optional[float] = None
    pv_terminal_value: Optional[float] = None
    enterprise_value: Optional[float] = None
    equity_value: Optional[float] = None
    implied_price: Optional[float] = None
    shares_outstanding: Optional[float] = None
    # Keep these for backward-compat with frontend
    projected_revenues: List[float] = []
    projected_fcf: List[float] = []


class SensitivityMatrix(BaseModel):
    row_label: str
    col_label: str
    row_values: List[float]
    col_values: List[float]
    matrix: List[List[Optional[float]]]


class DCFResponse(BaseModel):
    ticker: str
    currency: str = "USD"
    base_case: DCFScenario
    conservative_case: DCFScenario
    optimistic_case: DCFScenario
    sensitivity: SensitivityMatrix
    methodology_note: str = (
        "DCF analysis uses EBIT-based NOPAT: FCF = (EBITDA - D&A) x (1 - tax_rate) - CapEx - DNWC. "
        "Terminal value via Gordon Growth Model. All assumptions are user-defined and purely illustrative. "
        "This does not represent a target price, fair value, or investment recommendation. "
        "Small changes in WACC or terminal growth rate can materially affect implied valuations."
    )
    generated_at: Optional[str] = None
