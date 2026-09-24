"""
Tests for financial calculation logic.
These are deterministic — no mocking of external services.
"""

import pytest
from app.api.v1.valuation import _run_dcf
from app.schemas.valuation import DCFAssumptions


def make_assumptions(**overrides) -> DCFAssumptions:
    defaults = {
        "revenue_growth_rates": [0.10, 0.10, 0.10, 0.10, 0.10],
        "ebitda_margin": 0.25,
        "tax_rate": 0.21,
        "capex_pct_revenue": 0.05,
        "nwc_change_pct_revenue": 0.02,
        "wacc": 0.10,
        "terminal_growth_rate": 0.025,
        "base_revenue": 1000.0,
    }
    defaults.update(overrides)
    return DCFAssumptions(**defaults)


def test_dcf_produces_positive_enterprise_value():
    a = make_assumptions()
    result = _run_dcf(a)
    assert result.enterprise_value is not None
    assert result.enterprise_value > 0


def test_dcf_higher_wacc_lower_value():
    low_wacc = _run_dcf(make_assumptions(wacc=0.08))
    high_wacc = _run_dcf(make_assumptions(wacc=0.14))
    assert low_wacc.enterprise_value > high_wacc.enterprise_value


def test_dcf_higher_growth_higher_value():
    low_growth = _run_dcf(make_assumptions(revenue_growth_rates=[0.03] * 5))
    high_growth = _run_dcf(make_assumptions(revenue_growth_rates=[0.20] * 5))
    assert high_growth.enterprise_value > low_growth.enterprise_value


def test_dcf_correct_revenue_projection():
    a = make_assumptions(base_revenue=1000.0, revenue_growth_rates=[0.10, 0.10, 0.10, 0.10, 0.10])
    result = _run_dcf(a)
    # Year 1 revenue: 1000 * 1.10 = 1100
    assert abs(result.projected_revenues[0] - 1100.0) < 0.01


def test_dcf_terminal_growth_exceeds_wacc_raises():
    """Terminal growth >= WACC causes division by zero or negative TV."""
    a = make_assumptions(wacc=0.05, terminal_growth_rate=0.06)
    with pytest.raises(Exception):
        _run_dcf(a)


def test_dcf_zero_revenue_growth():
    a = make_assumptions(revenue_growth_rates=[0.0] * 5, base_revenue=500.0)
    result = _run_dcf(a)
    # Revenue should stay at 500
    for rev in result.projected_revenues:
        assert abs(rev - 500.0) < 0.01
