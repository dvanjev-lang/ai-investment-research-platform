"""
Tests for financial ratio calculations via MockDataProvider.
"""

import pytest
import asyncio
from app.data.mock_provider import MockDataProvider


@pytest.fixture
def provider():
    return MockDataProvider()


def run(coro):
    return asyncio.run(coro)


def test_gross_margin_between_zero_and_one(provider):
    ratios = run(provider.get_financial_ratios("NVDA"))
    for r in ratios:
        if r.gross_margin is not None:
            assert 0 < r.gross_margin < 1, f"Gross margin out of range: {r.gross_margin}"


def test_operating_margin_less_than_gross_margin(provider):
    ratios = run(provider.get_financial_ratios("NVDA"))
    for r in ratios:
        if r.gross_margin and r.operating_margin:
            assert r.operating_margin <= r.gross_margin


def test_revenue_growth_is_reasonable(provider):
    ratios = run(provider.get_financial_ratios("NVDA"))
    for r in ratios:
        if r.revenue_growth is not None:
            assert -1.0 < r.revenue_growth < 10.0, f"Suspicious revenue growth: {r.revenue_growth}"


def test_debt_to_equity_non_negative(provider):
    ratios = run(provider.get_financial_ratios("NVDA"))
    for r in ratios:
        if r.debt_to_equity is not None:
            assert r.debt_to_equity >= 0


def test_mock_returns_income_statements(provider):
    income = run(provider.get_income_statements("NVDA"))
    assert len(income) > 0
    assert income[0].revenue is not None
    assert income[0].revenue > 0


def test_mock_search_returns_results(provider):
    results = run(provider.search_companies("nvidia"))
    assert len(results) > 0
    assert results[0].ticker == "NVDA"


def test_mock_unknown_ticker_returns_fallback(provider):
    company = run(provider.get_company("ZZZZ"))
    assert company is not None
    assert company.ticker == "ZZZZ"
