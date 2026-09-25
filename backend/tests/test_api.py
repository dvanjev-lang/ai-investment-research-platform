"""
API endpoint integration tests using FastAPI TestClient.

These tests hit actual routes and verify response shapes, status codes,
and data correctness — not just unit logic.
"""

import io
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_root_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_v1_health(self):
        r = client.get("/api/v1/health")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------

class TestCompanies:
    def test_search_returns_list(self):
        r = client.get("/api/v1/companies/search?q=apple")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "ticker" in data[0]
        assert "name" in data[0]

    def test_company_detail_structure(self):
        """GET /companies/{ticker} returns nested CompanyProfile shape."""
        r = client.get("/api/v1/companies/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "company" in data
        assert data["company"]["ticker"] == "AAPL"
        assert "sector" in data["company"]
        assert "quote" in data

    def test_company_detail_quote_has_price(self):
        r = client.get("/api/v1/companies/NVDA")
        assert r.status_code == 200
        data = r.json()
        assert data["quote"]["ticker"] == "NVDA"
        assert data["quote"]["price"] is not None

    def test_company_financials_income_statements(self):
        """GET /companies/{ticker}/financials returns income_statements."""
        r = client.get("/api/v1/companies/AAPL/financials")
        assert r.status_code == 200
        data = r.json()
        assert "income_statements" in data
        assert len(data["income_statements"]) > 0
        stmt = data["income_statements"][0]
        assert "revenue" in stmt
        assert stmt["revenue"] > 0

    def test_company_financials_ratios(self):
        r = client.get("/api/v1/companies/MSFT/financials")
        assert r.status_code == 200
        data = r.json()
        assert "ratios" in data
        assert len(data["ratios"]) > 0

    def test_company_financials_cashflow(self):
        r = client.get("/api/v1/companies/NVDA/financials")
        assert r.status_code == 200
        data = r.json()
        assert "cash_flows" in data

    def test_company_unknown_ticker_fallback(self):
        """Mock provider always returns a company — unknown ticker returns 200 with fallback data."""
        r = client.get("/api/v1/companies/XXXXXXXXXX")
        assert r.status_code == 200
        data = r.json()
        # Should still have valid structure
        assert "company" in data
        assert data["company"]["ticker"] == "XXXXXXXXXX"

    def test_company_peers(self):
        r = client.get("/api/v1/companies/NVDA/peers")
        assert r.status_code == 200
        data = r.json()
        assert "ticker" in data
        assert "peers" in data


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

class TestDocuments:
    def test_upload_txt_document(self):
        content = b"NVIDIA revenue grew 122% in fiscal 2024 driven by data center demand."
        r = client.post(
            "/api/v1/documents/upload",
            data={"ticker": "NVDA", "document_type": "annual_report"},
            files={"file": ("nvda_annual.txt", io.BytesIO(content), "text/plain")},
        )
        assert r.status_code == 200
        data = r.json()
        assert "document_id" in data
        assert data["ticker"] == "NVDA"
        assert data["chunk_count"] >= 1
        assert data["retrieval_mode"] in ("semantic", "tfidf")

    def test_upload_unsupported_extension_400(self):
        r = client.post(
            "/api/v1/documents/upload",
            data={"ticker": "AAPL"},
            files={"file": ("data.csv", io.BytesIO(b"a,b,c"), "text/csv")},
        )
        assert r.status_code == 400

    def test_upload_file_too_large_413(self):
        large_content = b"x" * (21 * 1024 * 1024)  # 21 MB
        r = client.post(
            "/api/v1/documents/upload",
            data={"ticker": "AAPL"},
            files={"file": ("big.txt", io.BytesIO(large_content), "text/plain")},
        )
        assert r.status_code == 413

    def test_list_documents_empty_for_unknown_ticker(self):
        r = client.get("/api/v1/documents/ZZZZ")
        assert r.status_code == 200
        assert r.json()["documents"] == []

    def test_list_documents_after_upload(self):
        content = b"Apple revenue report for fiscal year 2024."
        r = client.post(
            "/api/v1/documents/upload",
            data={"ticker": "TESTLIST"},
            files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
        )
        assert r.status_code == 200
        r2 = client.get("/api/v1/documents/TESTLIST")
        assert r2.status_code == 200
        assert len(r2.json()["documents"]) >= 1

    def test_get_document_by_id(self):
        content = b"Cash flow from operations increased to $50 billion."
        upload = client.post(
            "/api/v1/documents/upload",
            data={"ticker": "DOCTEST"},
            files={"file": ("cf.txt", io.BytesIO(content), "text/plain")},
        )
        doc_id = upload.json()["document_id"]
        r = client.get(f"/api/v1/documents/document/{doc_id}")
        assert r.status_code == 200
        assert r.json()["id"] == doc_id

    def test_get_nonexistent_document_404(self):
        r = client.get("/api/v1/documents/document/does-not-exist-xyz")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Research
# ---------------------------------------------------------------------------

class TestResearch:
    def test_query_returns_answer(self):
        r = client.post("/api/v1/research/query", json={
            "ticker": "AAPL",
            "question": "What is the gross margin?",
            "include_financial_data": True,
        })
        assert r.status_code == 200
        data = r.json()
        assert "answer" in data
        assert len(data["answer"]) > 10
        assert "agent_trace" in data
        assert len(data["agent_trace"]) >= 2

    def test_query_includes_citations(self):
        r = client.post("/api/v1/research/query", json={
            "ticker": "MSFT",
            "question": "What is revenue?",
            "include_financial_data": True,
        })
        assert r.status_code == 200
        data = r.json()
        assert "citations" in data
        assert len(data["citations"]) >= 1
        # At least one citation should be financial_data type
        types = [c["source_type"] for c in data["citations"]]
        assert "financial_data" in types

    def test_query_disclaimer_present(self):
        r = client.post("/api/v1/research/query", json={
            "ticker": "NVDA",
            "question": "What is the operating margin?",
            "include_financial_data": True,
        })
        data = r.json()
        assert "disclaimer" in data
        assert "investment advice" in data["disclaimer"].lower()

    def test_query_agent_trace_has_financial_step(self):
        r = client.post("/api/v1/research/query", json={
            "ticker": "NVDA",
            "question": "What is the net margin?",
            "include_financial_data": True,
        })
        data = r.json()
        agents = [step["agent"] for step in data["agent_trace"]]
        assert "Financial Data Agent" in agents

    def test_query_agent_trace_has_document_step(self):
        r = client.post("/api/v1/research/query", json={
            "ticker": "NVDA",
            "question": "What are the risk factors?",
            "include_financial_data": False,
        })
        data = r.json()
        agents = [step["agent"] for step in data["agent_trace"]]
        assert "Document Research Agent" in agents

    def test_report_returns_sections(self):
        r = client.post("/api/v1/research/report", json={"ticker": "AAPL"})
        assert r.status_code == 200
        data = r.json()
        assert data["ticker"] == "AAPL"
        assert "sections" in data
        titles = [s["title"] for s in data["sections"]]
        assert "Executive Summary" in titles
        assert "Financial Performance" in titles

    def test_report_has_company_name(self):
        r = client.post("/api/v1/research/report", json={"ticker": "MSFT"})
        data = r.json()
        assert "company_name" in data
        assert data["company_name"] == "Microsoft Corporation"


# ---------------------------------------------------------------------------
# Valuation (DCF)
# ---------------------------------------------------------------------------

class TestValuation:
    _BASE_PAYLOAD = {
        "base_revenue": 1000.0,
        "revenue_growth_rates": [0.15, 0.12, 0.10, 0.08, 0.06],
        "ebitda_margin": 0.25,
        "da_pct_revenue": 0.04,
        "tax_rate": 0.21,
        "capex_pct_revenue": 0.05,
        "nwc_change_pct_revenue": 0.02,
        "wacc": 0.10,
        "terminal_growth_rate": 0.025,
    }

    def test_dcf_returns_three_scenarios(self):
        r = client.post("/api/v1/valuation/AAPL/dcf", json=self._BASE_PAYLOAD)
        assert r.status_code == 200
        data = r.json()
        assert "base_case" in data
        assert "conservative_case" in data
        assert "optimistic_case" in data

    def test_dcf_base_case_has_projections(self):
        r = client.post("/api/v1/valuation/AAPL/dcf", json=self._BASE_PAYLOAD)
        data = r.json()
        projections = data["base_case"]["projections"]
        assert len(projections) == 5  # 5-year forecast

    def test_dcf_projections_have_correct_fields(self):
        r = client.post("/api/v1/valuation/AAPL/dcf", json=self._BASE_PAYLOAD)
        yr1 = r.json()["base_case"]["projections"][0]
        for field in ("year", "revenue", "ebitda", "da", "ebit", "nopat", "capex", "delta_nwc", "free_cash_flow", "pv_fcf"):
            assert field in yr1, f"Missing field: {field}"

    def test_dcf_nopat_uses_ebit_not_ebitda(self):
        """NOPAT = EBIT × (1 - t), not EBITDA × (1 - t). This catches the original formula bug."""
        r = client.post("/api/v1/valuation/AAPL/dcf", json=self._BASE_PAYLOAD)
        yr1 = r.json()["base_case"]["projections"][0]
        expected_nopat = (yr1["ebitda"] - yr1["da"]) * (1 - 0.21)
        wrong_nopat = yr1["ebitda"] * (1 - 0.21)
        assert abs(yr1["nopat"] - expected_nopat) < 0.01
        assert abs(yr1["nopat"] - wrong_nopat) > 1.0  # old buggy formula not used

    def test_dcf_ebit_equals_ebitda_minus_da(self):
        r = client.post("/api/v1/valuation/AAPL/dcf", json=self._BASE_PAYLOAD)
        yr1 = r.json()["base_case"]["projections"][0]
        assert abs(yr1["ebit"] - (yr1["ebitda"] - yr1["da"])) < 0.01

    def test_dcf_returns_sensitivity_matrix(self):
        r = client.post("/api/v1/valuation/AAPL/dcf", json=self._BASE_PAYLOAD)
        sens = r.json()["sensitivity"]
        assert "matrix" in sens
        assert len(sens["matrix"]) == 5   # 5 WACC rows
        assert len(sens["matrix"][0]) == 5  # 5 TGR cols

    def test_dcf_invalid_wacc_equals_tgr_422(self):
        payload = {**self._BASE_PAYLOAD, "wacc": 0.025, "terminal_growth_rate": 0.025}
        r = client.post("/api/v1/valuation/AAPL/dcf", json=payload)
        assert r.status_code == 422

    def test_dcf_invalid_spread_too_small_422(self):
        payload = {**self._BASE_PAYLOAD, "wacc": 0.030, "terminal_growth_rate": 0.025}
        r = client.post("/api/v1/valuation/AAPL/dcf", json=payload)
        assert r.status_code == 422

    def test_dcf_defaults_endpoint(self):
        r = client.get("/api/v1/valuation/AAPL/dcf/defaults")
        assert r.status_code == 200
        data = r.json()
        assert "defaults" in data
        defaults = data["defaults"]
        assert defaults["base_revenue"] > 0
        assert "wacc" in defaults
        assert "terminal_growth_rate" in defaults
        assert "revenue_growth_rates" in defaults

    def test_dcf_defaults_revenue_reflects_company_data(self):
        """AAPL defaults should use the mock income statement, not the hardcoded 1000 fallback."""
        r = client.get("/api/v1/valuation/AAPL/dcf/defaults")
        data = r.json()
        # Mock AAPL FY2024 revenue is 391,035M — well above the 1000 fallback
        assert data["defaults"]["base_revenue"] > 10_000.0

    def test_dcf_conservative_ev_less_than_base(self):
        r = client.post("/api/v1/valuation/NVDA/dcf", json=self._BASE_PAYLOAD)
        data = r.json()
        base_ev = data["base_case"]["enterprise_value"]
        cons_ev = data["conservative_case"]["enterprise_value"]
        assert cons_ev < base_ev

    def test_dcf_optimistic_ev_greater_than_base(self):
        r = client.post("/api/v1/valuation/NVDA/dcf", json=self._BASE_PAYLOAD)
        data = r.json()
        base_ev = data["base_case"]["enterprise_value"]
        opt_ev = data["optimistic_case"]["enterprise_value"]
        assert opt_ev > base_ev
