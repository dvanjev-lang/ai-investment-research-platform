"""
Tests for the DCF valuation engine.

Validates the EBIT-based NOPAT formula:
    EBIT   = Revenue x (EBITDA_margin - DA_pct)
    NOPAT  = EBIT x (1 - tax_rate)
    FCF    = NOPAT - CapEx - DNWC
    TV     = FCF_n x (1 + g) / (WACC - g)
    EV     = SUM PV(FCF_t) + PV(TV)
"""

import pytest
import math
from app.api.v1.valuation import _run_dcf, _sensitivity_cell
from app.schemas.valuation import DCFAssumptions


# ────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────

def make_assumptions(**overrides) -> DCFAssumptions:
    """Return valid base assumptions, optionally overriding fields."""
    defaults = dict(
        revenue_growth_rates=[0.10, 0.10, 0.10, 0.10, 0.10],
        ebitda_margin=0.30,
        da_pct_revenue=0.05,
        tax_rate=0.21,
        capex_pct_revenue=0.05,
        nwc_change_pct_revenue=0.02,
        wacc=0.10,
        terminal_growth_rate=0.025,
        base_revenue=1000.0,
    )
    defaults.update(overrides)
    return DCFAssumptions(**defaults)


# ────────────────────────────────────────────────
# Formula correctness
# ────────────────────────────────────────────────

def test_ebit_equals_ebitda_minus_da():
    """Year-1 EBIT must equal EBITDA - D&A."""
    a = make_assumptions(
        base_revenue=1000.0,
        revenue_growth_rates=[0.10, 0.10, 0.10, 0.10, 0.10],
        ebitda_margin=0.30,
        da_pct_revenue=0.05,
    )
    result = _run_dcf(a)
    yr1 = result.projections[0]
    expected_ebitda = yr1.revenue * 0.30
    expected_da = yr1.revenue * 0.05
    expected_ebit = expected_ebitda - expected_da
    assert abs(yr1.ebitda - expected_ebitda) < 0.01, f"EBITDA mismatch: {yr1.ebitda} vs {expected_ebitda}"
    assert abs(yr1.da - expected_da) < 0.01, f"D&A mismatch: {yr1.da} vs {expected_da}"
    assert abs(yr1.ebit - expected_ebit) < 0.01, f"EBIT mismatch: {yr1.ebit} vs {expected_ebit}"


def test_nopat_uses_ebit_not_ebitda():
    """NOPAT must be EBIT x (1-t), NOT EBITDA x (1-t)."""
    a = make_assumptions(
        base_revenue=1000.0,
        revenue_growth_rates=[0.10, 0.10, 0.10, 0.10, 0.10],
        ebitda_margin=0.30,
        da_pct_revenue=0.05,
        tax_rate=0.21,
    )
    result = _run_dcf(a)
    yr1 = result.projections[0]
    rev = yr1.revenue

    correct_nopat = rev * (0.30 - 0.05) * (1 - 0.21)
    wrong_nopat   = rev * 0.30 * (1 - 0.21)   # the old buggy formula

    assert abs(yr1.nopat - correct_nopat) < 0.01, (
        f"NOPAT = {yr1.nopat:.2f} but expected EBIT-based NOPAT = {correct_nopat:.2f}. "
        f"(Old EBITDA-based formula would give {wrong_nopat:.2f})"
    )
    assert abs(yr1.nopat - wrong_nopat) > 1.0, (
        "NOPAT equals EBITDA x (1-t) — the old formula is still being used!"
    )


def test_fcf_formula():
    """FCF = NOPAT - CapEx - DNWC."""
    a = make_assumptions()
    result = _run_dcf(a)
    for p in result.projections:
        expected_fcf = p.nopat - p.capex - p.delta_nwc
        assert abs(p.free_cash_flow - expected_fcf) < 0.01, (
            f"Year {p.year}: FCF {p.free_cash_flow:.2f} != NOPAT - CapEx - DNWC = {expected_fcf:.2f}"
        )


def test_revenue_compounding():
    """Each year's revenue = prior year x (1 + growth rate)."""
    a = make_assumptions(
        base_revenue=1000.0,
        revenue_growth_rates=[0.10, 0.20, 0.05, 0.08, 0.12],
    )
    result = _run_dcf(a)
    rev = 1000.0
    for p, g in zip(result.projections, [0.10, 0.20, 0.05, 0.08, 0.12]):
        rev *= (1 + g)
        assert abs(p.revenue - rev) < 0.01


def test_pv_discounting():
    """PV(FCF_t) = FCF_t / (1 + WACC)^t."""
    a = make_assumptions(wacc=0.10)
    result = _run_dcf(a)
    for p in result.projections:
        expected_pv = p.free_cash_flow / (1 + 0.10) ** p.year
        assert abs(p.pv_fcf - expected_pv) < 0.01


def test_terminal_value_gordon_growth():
    """TV = FCF_n x (1 + g) / (WACC - g)."""
    a = make_assumptions(wacc=0.10, terminal_growth_rate=0.025)
    result = _run_dcf(a)
    last_fcf = result.projections[-1].free_cash_flow
    expected_tv = last_fcf * (1 + 0.025) / (0.10 - 0.025)
    assert abs(result.terminal_value - expected_tv) < 0.10


def test_enterprise_value_equals_pv_fcfs_plus_pv_tv():
    """EV = SUM PV(FCF) + PV(TV)."""
    a = make_assumptions()
    result = _run_dcf(a)
    sum_pv_fcfs = sum(p.pv_fcf for p in result.projections)
    expected_ev = sum_pv_fcfs + result.pv_terminal_value
    assert abs(result.enterprise_value - expected_ev) < 0.10


# ────────────────────────────────────────────────
# Monotonicity / economic logic
# ────────────────────────────────────────────────

def test_higher_wacc_produces_lower_ev():
    """All else equal, higher WACC lower EV (time value of money)."""
    low  = _run_dcf(make_assumptions(wacc=0.08))
    high = _run_dcf(make_assumptions(wacc=0.14))
    assert low.enterprise_value > high.enterprise_value


def test_higher_revenue_growth_produces_higher_ev():
    low  = _run_dcf(make_assumptions(revenue_growth_rates=[0.03] * 5))
    high = _run_dcf(make_assumptions(revenue_growth_rates=[0.20] * 5))
    assert high.enterprise_value > low.enterprise_value


def test_higher_da_reduces_nopat_and_ev():
    """Higher D&A reduces EBIT reduces NOPAT reduces FCF reduces EV."""
    low_da  = _run_dcf(make_assumptions(da_pct_revenue=0.02))
    high_da = _run_dcf(make_assumptions(da_pct_revenue=0.08))
    assert low_da.enterprise_value > high_da.enterprise_value


def test_zero_revenue_growth_stable_revenues():
    a = make_assumptions(base_revenue=500.0, revenue_growth_rates=[0.0] * 5)
    result = _run_dcf(a)
    for p in result.projections:
        assert abs(p.revenue - 500.0) < 0.01


# ────────────────────────────────────────────────
# Validation guards
# ────────────────────────────────────────────────

def test_wacc_equal_to_tgr_raises_validation_error():
    """WACC = TGR makes denominator zero — must be rejected."""
    with pytest.raises(ValueError, match="WACC.*must exceed"):
        make_assumptions(wacc=0.025, terminal_growth_rate=0.025)


def test_wacc_less_than_tgr_raises():
    with pytest.raises(ValueError):
        make_assumptions(wacc=0.02, terminal_growth_rate=0.03)


def test_wacc_tgr_spread_too_small_raises():
    """Spread < 1% is considered unsafe."""
    with pytest.raises(ValueError, match="spread"):
        make_assumptions(wacc=0.100, terminal_growth_rate=0.095)


def test_da_exceeds_ebitda_raises():
    """D&A >= EBITDA margin would produce negative EBIT — must be rejected."""
    with pytest.raises(ValueError, match="D&A"):
        make_assumptions(ebitda_margin=0.10, da_pct_revenue=0.12)


def test_negative_base_revenue_raises():
    with pytest.raises(Exception):  # Pydantic gt=0 validation
        make_assumptions(base_revenue=-100.0)


def test_zero_base_revenue_raises():
    with pytest.raises(Exception):
        make_assumptions(base_revenue=0.0)


def test_tax_rate_above_99pct_raises():
    with pytest.raises(Exception):
        make_assumptions(tax_rate=1.5)


# ────────────────────────────────────────────────
# Sensitivity matrix
# ────────────────────────────────────────────────

def test_sensitivity_cell_returns_none_for_invalid_spread():
    a = make_assumptions(wacc=0.10, terminal_growth_rate=0.025)
    result = _sensitivity_cell(a, wacc=0.02, tgr=0.025)  # spread = 0.005 < 0.01
    assert result is None  # too small spread invalid


def test_sensitivity_cell_valid():
    a = make_assumptions()
    result = _sensitivity_cell(a, wacc=0.10, tgr=0.02)
    assert result is not None
    assert result > 0


def test_sensitivity_monotone_along_wacc_axis():
    """Along a fixed TGR column, increasing WACC must decrease EV."""
    a = make_assumptions(terminal_growth_rate=0.02)
    ev_low  = _sensitivity_cell(a, wacc=0.08, tgr=0.02)
    ev_mid  = _sensitivity_cell(a, wacc=0.10, tgr=0.02)
    ev_high = _sensitivity_cell(a, wacc=0.12, tgr=0.02)
    assert ev_low > ev_mid > ev_high
