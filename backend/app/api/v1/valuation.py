from fastapi import APIRouter, HTTPException
from datetime import datetime
import math

from app.schemas.valuation import DCFAssumptions, DCFResponse, DCFScenario, SensitivityMatrix
from app.data.provider_factory import get_data_provider

router = APIRouter()


def _run_dcf(assumptions: DCFAssumptions) -> DCFScenario:
    revenues = []
    rev = assumptions.base_revenue
    for g in assumptions.revenue_growth_rates:
        rev = rev * (1 + g)
        revenues.append(round(rev, 2))

    fcfs = []
    for rev in revenues:
        ebitda = rev * assumptions.ebitda_margin
        nopat = ebitda * (1 - assumptions.tax_rate)
        capex = rev * assumptions.capex_pct_revenue
        nwc = rev * assumptions.nwc_change_pct_revenue
        fcf = nopat - capex - nwc
        fcfs.append(round(fcf, 2))

    # Terminal value (Gordon Growth)
    terminal_fcf = fcfs[-1] * (1 + assumptions.terminal_growth_rate)
    tv = terminal_fcf / (assumptions.wacc - assumptions.terminal_growth_rate)

    # PV of FCFs
    pv_fcfs = sum(fcf / (1 + assumptions.wacc) ** (i + 1) for i, fcf in enumerate(fcfs))
    pv_tv = tv / (1 + assumptions.wacc) ** len(fcfs)
    ev = pv_fcfs + pv_tv

    return DCFScenario(
        name="",
        assumptions=assumptions,
        projected_revenues=revenues,
        projected_fcf=fcfs,
        terminal_value=round(tv, 2),
        enterprise_value=round(ev, 2),
    )


@router.post("/{ticker}/dcf", response_model=DCFResponse)
async def run_dcf(ticker: str, base_assumptions: DCFAssumptions):
    ticker = ticker.upper()

    base = _run_dcf(base_assumptions)
    base.name = "Base Case"

    cons_assumptions = base_assumptions.model_copy(update={
        "revenue_growth_rates": [max(g - 0.05, 0.0) for g in base_assumptions.revenue_growth_rates],
        "ebitda_margin": base_assumptions.ebitda_margin - 0.03,
        "wacc": base_assumptions.wacc + 0.01,
        "terminal_growth_rate": max(base_assumptions.terminal_growth_rate - 0.005, 0.0),
    })
    conservative = _run_dcf(cons_assumptions)
    conservative.name = "Conservative Case"

    opt_assumptions = base_assumptions.model_copy(update={
        "revenue_growth_rates": [g + 0.05 for g in base_assumptions.revenue_growth_rates],
        "ebitda_margin": base_assumptions.ebitda_margin + 0.03,
        "wacc": base_assumptions.wacc - 0.01,
        "terminal_growth_rate": base_assumptions.terminal_growth_rate + 0.005,
    })
    optimistic = _run_dcf(opt_assumptions)
    optimistic.name = "Optimistic Case"

    # Sensitivity: WACC vs terminal growth
    waccs = [base_assumptions.wacc - 0.02, base_assumptions.wacc - 0.01, base_assumptions.wacc, base_assumptions.wacc + 0.01, base_assumptions.wacc + 0.02]
    tgrs = [0.01, 0.015, 0.02, 0.025, 0.03]
    matrix = []
    for w in waccs:
        row = []
        for tg in tgrs:
            try:
                a = base_assumptions.model_copy(update={"wacc": w, "terminal_growth_rate": tg})
                s = _run_dcf(a)
                row.append(round(s.enterprise_value or 0, 0))
            except Exception:
                row.append(0.0)
        matrix.append(row)

    sensitivity = SensitivityMatrix(
        row_label="WACC",
        col_label="Terminal Growth Rate",
        row_values=waccs,
        col_values=tgrs,
        matrix=matrix,
    )

    return DCFResponse(
        ticker=ticker,
        base_case=base,
        conservative_case=conservative,
        optimistic_case=optimistic,
        sensitivity=sensitivity,
        generated_at=datetime.utcnow().isoformat(),
    )
