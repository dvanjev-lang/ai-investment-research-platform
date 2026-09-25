"""
DCF Valuation Engine — AI Investment Research Platform

Formula reference:
    EBIT   = Revenue x EBITDA_margin - Revenue x DA_pct
           = Revenue x (EBITDA_margin - DA_pct)
    NOPAT  = EBIT x (1 - tax_rate)
    FCF    = NOPAT - CapEx - DNWC
           = NOPAT - Revenue x capex_pct - Revenue x nwc_change_pct

    Terminal Value (Gordon Growth):
        TV = FCF_n x (1 + g) / (WACC - g)
        where WACC > g  [enforced by schema validator]

    Enterprise Value:
        EV = SUM [FCF_t / (1 + WACC)^t] + TV / (1 + WACC)^n

All inputs in millions (same currency). Output in same currency.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional

from app.schemas.valuation import (
    DCFAssumptions, DCFResponse, DCFScenario, DCFYearProjection,
    SensitivityMatrix
)
from app.data.provider_factory import get_data_provider

router = APIRouter()


class DCFValidationError(ValueError):
    pass


def _run_dcf(assumptions: DCFAssumptions, scenario_name: str = "") -> DCFScenario:
    """
    Run a single DCF scenario.

    Returns a DCFScenario with full year-by-year projections for transparency.
    All values in the same currency unit as base_revenue (millions).

    Raises DCFValidationError for inputs that would produce meaningless output.
    """
    # Validate spread (also enforced by Pydantic validator, but explicit here)
    spread = assumptions.wacc - assumptions.terminal_growth_rate
    if spread <= 0:
        raise DCFValidationError(
            f"WACC ({assumptions.wacc:.1%}) must exceed terminal growth rate "
            f"({assumptions.terminal_growth_rate:.1%})"
        )

    projections: list[DCFYearProjection] = []
    rev = assumptions.base_revenue

    for year_idx, growth_rate in enumerate(assumptions.revenue_growth_rates, start=1):
        rev = rev * (1.0 + growth_rate)

        ebitda = rev * assumptions.ebitda_margin
        da = rev * assumptions.da_pct_revenue
        ebit = ebitda - da                          # EBIT = EBITDA - D&A
        nopat = ebit * (1.0 - assumptions.tax_rate) # NOPAT = EBIT x (1 - t)
        capex = rev * assumptions.capex_pct_revenue
        delta_nwc = rev * assumptions.nwc_change_pct_revenue
        fcf = nopat - capex - delta_nwc             # FCF = NOPAT - CapEx - DNWC

        pv_fcf = fcf / (1.0 + assumptions.wacc) ** year_idx

        projections.append(DCFYearProjection(
            year=year_idx,
            revenue=round(rev, 2),
            ebitda=round(ebitda, 2),
            da=round(da, 2),
            ebit=round(ebit, 2),
            nopat=round(nopat, 2),
            capex=round(capex, 2),
            delta_nwc=round(delta_nwc, 2),
            free_cash_flow=round(fcf, 2),
            pv_fcf=round(pv_fcf, 2),
        ))

    # Terminal value: Gordon Growth on year-n FCF
    terminal_fcf = projections[-1].free_cash_flow * (1.0 + assumptions.terminal_growth_rate)
    tv = terminal_fcf / (assumptions.wacc - assumptions.terminal_growth_rate)
    pv_tv = tv / (1.0 + assumptions.wacc) ** len(projections)

    ev = sum(p.pv_fcf for p in projections) + pv_tv

    return DCFScenario(
        name=scenario_name,
        assumptions=assumptions,
        projections=projections,
        terminal_value=round(tv, 2),
        pv_terminal_value=round(pv_tv, 2),
        enterprise_value=round(ev, 2),
        # Convenience lists for frontend charts
        projected_revenues=[p.revenue for p in projections],
        projected_fcf=[p.free_cash_flow for p in projections],
    )


def _sensitivity_cell(base_assumptions: DCFAssumptions, wacc: float, tgr: float) -> Optional[float]:
    """Compute EV for one cell of the sensitivity matrix. Returns None if inputs are invalid."""
    try:
        a = base_assumptions.model_copy(update={"wacc": round(wacc, 4), "terminal_growth_rate": round(tgr, 4)})
        s = _run_dcf(a)
        return round(s.enterprise_value, 0) if s.enterprise_value is not None else None
    except (ValueError, DCFValidationError):
        return None


@router.get("/{ticker}/dcf/defaults")
async def get_dcf_defaults(ticker: str):
    """
    Return sensible default DCF assumptions for a given company,
    pre-filled with the company's most recent annual revenue and
    estimated D&A from financial statements.
    """
    ticker = ticker.upper()
    provider = get_data_provider()
    income = await provider.get_income_statements(ticker, period="annual", limit=2)

    base_revenue = 1000.0  # fallback
    ebitda_margin = 0.20
    da_pct_revenue = 0.04
    currency = "USD"
    data_note = "Default assumptions (no company data available)"

    if income:
        latest = income[0]
        if latest.revenue and latest.revenue > 0:
            base_revenue = latest.revenue
            data_note = f"Base revenue from FY{latest.fiscal_year} annual report"
        if latest.ebitda and latest.revenue:
            ebitda_margin = round(latest.ebitda / latest.revenue, 4)
        if latest.depreciation_amortization and latest.revenue:
            da_pct_revenue = round(latest.depreciation_amortization / latest.revenue, 4)

    company = await provider.get_company(ticker)
    if company:
        currency = company.currency or "USD"

    return {
        "ticker": ticker,
        "currency": currency,
        "defaults": {
            "base_revenue": base_revenue,
            "ebitda_margin": ebitda_margin,
            "da_pct_revenue": da_pct_revenue,
            "tax_rate": 0.21,
            "capex_pct_revenue": 0.05,
            "nwc_change_pct_revenue": 0.02,
            "wacc": 0.10,
            "terminal_growth_rate": 0.025,
            "revenue_growth_rates": [0.12, 0.10, 0.08, 0.07, 0.06],
        },
        "data_note": data_note,
        "data_source": "Demo data (illustrative)",
        "disclaimer": (
            "Assumptions are pre-filled from historical data as a starting point only. "
            "All values should be independently researched and adjusted."
        ),
    }


@router.post("/{ticker}/dcf", response_model=DCFResponse)
async def run_dcf(ticker: str, base_assumptions: DCFAssumptions):
    """
    Run a 3-scenario DCF analysis for the given ticker.

    The Base Case uses the provided assumptions exactly.
    Conservative/Optimistic cases apply symmetric adjustments.
    A WACC x Terminal Growth Rate sensitivity matrix is also returned.

    All values in millions (same currency as base_revenue input).
    """
    ticker = ticker.upper()

    # Base case
    try:
        base = _run_dcf(base_assumptions, "Base Case")
    except (ValueError, DCFValidationError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Conservative: lower growth, lower margin, higher WACC, lower TGR
    cons_growth = [max(g - 0.05, 0.0) for g in base_assumptions.revenue_growth_rates]
    cons_ebitda = max(base_assumptions.ebitda_margin - 0.03, base_assumptions.da_pct_revenue + 0.02)
    cons_wacc = min(base_assumptions.wacc + 0.01, 0.40)
    cons_tgr = max(base_assumptions.terminal_growth_rate - 0.005, 0.0)
    try:
        cons_a = base_assumptions.model_copy(update={
            "revenue_growth_rates": cons_growth,
            "ebitda_margin": cons_ebitda,
            "wacc": cons_wacc,
            "terminal_growth_rate": cons_tgr,
        })
        conservative = _run_dcf(cons_a, "Conservative Case")
    except (ValueError, DCFValidationError) as e:
        # If conservative scenario is invalid, use base assumptions with note
        conservative = _run_dcf(base_assumptions, f"Conservative Case (adjusted: {e})")

    # Optimistic: higher growth, higher margin, lower WACC, higher TGR
    opt_growth = [g + 0.05 for g in base_assumptions.revenue_growth_rates]
    opt_ebitda = min(base_assumptions.ebitda_margin + 0.03, 0.95)
    opt_wacc = max(base_assumptions.wacc - 0.01, base_assumptions.terminal_growth_rate + 0.015)
    opt_tgr = min(base_assumptions.terminal_growth_rate + 0.005, base_assumptions.wacc - 0.015)
    try:
        opt_a = base_assumptions.model_copy(update={
            "revenue_growth_rates": opt_growth,
            "ebitda_margin": opt_ebitda,
            "wacc": opt_wacc,
            "terminal_growth_rate": opt_tgr,
        })
        optimistic = _run_dcf(opt_a, "Optimistic Case")
    except (ValueError, DCFValidationError) as e:
        optimistic = _run_dcf(base_assumptions, f"Optimistic Case (adjusted: {e})")

    # Sensitivity matrix: WACC (rows) x Terminal Growth Rate (cols)
    wacc_range = [
        round(base_assumptions.wacc - 0.02, 4),
        round(base_assumptions.wacc - 0.01, 4),
        round(base_assumptions.wacc,        4),
        round(base_assumptions.wacc + 0.01, 4),
        round(base_assumptions.wacc + 0.02, 4),
    ]
    tgr_range = [0.010, 0.015, 0.020, 0.025, 0.030]

    matrix = [
        [_sensitivity_cell(base_assumptions, w, t) for t in tgr_range]
        for w in wacc_range
    ]

    sensitivity = SensitivityMatrix(
        row_label="WACC",
        col_label="Terminal Growth Rate",
        row_values=wacc_range,
        col_values=tgr_range,
        matrix=matrix,
    )

    return DCFResponse(
        ticker=ticker,
        base_case=base,
        conservative_case=conservative,
        optimistic_case=optimistic,
        sensitivity=sensitivity,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
