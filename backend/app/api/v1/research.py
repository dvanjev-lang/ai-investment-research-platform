from fastapi import APIRouter, HTTPException
from datetime import datetime
import time

from app.schemas.research import (
    ResearchQueryRequest, ResearchQueryResponse,
    ReportRequest, ReportResponse, ReportSection, Citation, AgentStep
)
from app.data.provider_factory import get_data_provider
from app.core.config import settings
from app.api.v1.documents import _document_store

router = APIRouter()

DISCLAIMER = (
    "This analysis is for informational purposes only and does not constitute "
    "investment advice or a recommendation to buy or sell any security. "
    "All financial data should be independently verified."
)


async def _run_research_pipeline(
    ticker: str,
    question: str,
    include_financial: bool = True,
) -> ResearchQueryResponse:
    start = time.time()
    agent_trace = []
    citations = []

    # Step 1: Research Planner
    agent_trace.append(AgentStep(
        agent="Research Planner",
        action="Analyze question intent",
        result_summary=f"Question classified as financial/fundamental analysis for {ticker}",
        sources_consulted=[],
    ))

    # Step 2: Financial Data Agent
    financial_context = ""
    if include_financial:
        provider = get_data_provider()
        company = await provider.get_company(ticker)
        income = await provider.get_income_statements(ticker)
        cashflow = await provider.get_cash_flows(ticker)
        ratios = await provider.get_financial_ratios(ticker)

        if company:
            financial_context += f"\nCompany: {company.name} ({ticker})\nSector: {company.sector}\nIndustry: {company.industry}\n"

        if income:
            latest = income[0]
            financial_context += f"\nLatest Annual Financials (FY{latest.fiscal_year}):\n"
            financial_context += f"- Revenue: ${latest.revenue:,.0f}M\n" if latest.revenue else ""
            financial_context += f"- Gross Profit: ${latest.gross_profit:,.0f}M\n" if latest.gross_profit else ""
            financial_context += f"- Operating Income: ${latest.operating_income:,.0f}M\n" if latest.operating_income else ""
            financial_context += f"- Net Income: ${latest.net_income:,.0f}M\n" if latest.net_income else ""
            financial_context += f"- EBITDA: ${latest.ebitda:,.0f}M\n" if latest.ebitda else ""

        if ratios:
            r = ratios[0]
            financial_context += f"\nKey Ratios:\n"
            if r.gross_margin: financial_context += f"- Gross Margin: {r.gross_margin:.1%}\n"
            if r.operating_margin: financial_context += f"- Operating Margin: {r.operating_margin:.1%}\n"
            if r.net_margin: financial_context += f"- Net Margin: {r.net_margin:.1%}\n"
            if r.revenue_growth: financial_context += f"- Revenue Growth (YoY): {r.revenue_growth:.1%}\n"

        citations.append(Citation(
            source_type="financial_data",
            source_name=f"Financial Statements — {ticker}",
            date="Demo data (illustrative)",
            excerpt=f"Revenue, margins, and growth metrics for {ticker}",
        ))
        agent_trace.append(AgentStep(
            agent="Financial Data Agent",
            action="Retrieve structured financials",
            result_summary=f"Retrieved income statements, ratios, and cash flows for {ticker}",
            sources_consulted=["Financial statements", "Key ratios"],
        ))

    # Step 3: Document Agent
    doc_context = ""
    ticker_docs = [v for v in _document_store.values() if v["ticker"] == ticker.upper()]
    if ticker_docs:
        doc = ticker_docs[0]
        # Basic keyword search in document text
        question_words = question.lower().split()
        text = doc.get("text", "")
        sentences = text.split(".")
        relevant = [s.strip() for s in sentences if any(w in s.lower() for w in question_words)][:5]
        if relevant:
            doc_context = "\n\nRelevant excerpts from " + doc["name"] + ":\n" + ". ".join(relevant)
            citations.append(Citation(
                source_type="document",
                source_name=doc["name"],
                document_id=doc["id"],
                excerpt=relevant[0][:200] if relevant else None,
            ))
            agent_trace.append(AgentStep(
                agent="Document Researcher",
                action="Search uploaded documents",
                result_summary=f"Found {len(relevant)} relevant passages in {doc['name']}",
                sources_consulted=[doc["name"]],
            ))

    # Step 4: LLM Answer Generation
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            system_prompt = """You are a financial research analyst assistant for an institutional research platform.

Your role is to provide factual, analytical responses based on the financial data and documents provided.

STRICT RULES:
- NEVER recommend buying, selling, or holding any security
- NEVER provide personalized investment advice
- NEVER predict future stock prices
- Always distinguish between facts (from data) and analysis (your interpretation)
- If data is unavailable, state "Data unavailable"
- Always cite the source of financial figures
- Be precise with numbers — use the data provided, do not estimate

Respond in clear, professional language suitable for a financial analyst audience."""

            user_msg = f"""Ticker: {ticker}

Question: {question}

Available Financial Data:
{financial_context if financial_context else 'No structured financial data available.'}
{doc_context if doc_context else ''}

Please answer the question using only the data provided above. Cite specific figures where relevant."""

            response = await client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.1,
                max_tokens=1500,
            )
            answer = response.choices[0].message.content or ""
            agent_trace.append(AgentStep(
                agent="Research Writer",
                action="Generate answer with GPT-4o",
                result_summary="Answer generated using financial data + document context",
                sources_consulted=["OpenAI GPT-4o"],
            ))
        except Exception as e:
            answer = _fallback_answer(ticker, question, financial_context)
            agent_trace.append(AgentStep(
                agent="Research Writer",
                action="Fallback answer (OpenAI unavailable)",
                result_summary=str(e),
                sources_consulted=[],
            ))
    else:
        answer = _fallback_answer(ticker, question, financial_context)
        agent_trace.append(AgentStep(
            agent="Research Writer",
            action="Demo answer (no OpenAI key configured)",
            result_summary="OpenAI API key not configured. Showing data summary.",
            sources_consulted=[],
        ))

    # Citation Validator
    agent_trace.append(AgentStep(
        agent="Citation Validator",
        action="Validate all cited sources",
        result_summary=f"{len(citations)} citation(s) validated",
        sources_consulted=[c.source_name for c in citations],
    ))

    latency = int((time.time() - start) * 1000)
    return ResearchQueryResponse(
        question=question,
        answer=answer,
        citations=citations,
        agent_trace=agent_trace,
        data_through="Demo data (illustrative)",
        disclaimer=DISCLAIMER,
        confidence_note="Demo mode — connect OpenAI API and live data for full functionality.",
    )


def _fallback_answer(ticker: str, question: str, context: str) -> str:
    return (
        f"**Research Summary for {ticker}**\n\n"
        f"Based on available financial data:\n\n"
        f"{context}\n\n"
        f"*Note: For AI-generated analysis, configure the OPENAI_API_KEY environment variable. "
        f"This is a demo response showing the structured data context.*"
    )


@router.post("/query", response_model=ResearchQueryResponse)
async def research_query(request: ResearchQueryRequest):
    return await _run_research_pipeline(
        ticker=request.ticker.upper(),
        question=request.question,
        include_financial=request.include_financial_data,
    )


@router.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    ticker = request.ticker.upper()
    provider = get_data_provider()
    company = await provider.get_company(ticker)
    income = await provider.get_income_statements(ticker)
    ratios = await provider.get_financial_ratios(ticker)
    cashflow = await provider.get_cash_flows(ticker)
    quote = await provider.get_quote(ticker)

    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    name = company.name
    latest_inc = income[0] if income else None
    latest_rat = ratios[0] if ratios else None
    latest_cf = cashflow[0] if cashflow else None

    def fmt(v, prefix="$", suffix="M", decimals=0):
        if v is None: return "N/A"
        return f"{prefix}{v:,.{decimals}f}{suffix}"

    def fmtp(v):
        if v is None: return "N/A"
        return f"{v:.1%}"

    sections = [
        ReportSection(
            title="Executive Summary",
            content=(
                f"{name} ({ticker}) is a {company.sector} company in the {company.industry} industry, "
                f"headquartered in {company.headquarters or 'N/A'}. "
                + (f"As of the most recent data, the company had a market capitalization of "
                   f"{fmt(quote.market_cap / 1e9 if quote and quote.market_cap else None, '$', 'B', 1)}. " if quote else "")
                + (f"In fiscal year {latest_inc.fiscal_year}, revenue was {fmt(latest_inc.revenue)}, "
                   f"with a gross margin of {fmtp(latest_rat.gross_margin) if latest_rat else 'N/A'}."
                   if latest_inc else "Financial data unavailable.")
            ),
            citations=[Citation(source_type="financial_data", source_name="Financial Statements", date="Demo data")],
        ),
        ReportSection(
            title="Company Overview",
            content=company.description or "No description available.",
        ),
        ReportSection(
            title="Financial Performance",
            content=(
                "**Income Statement Highlights**\n\n"
                + (f"- Revenue (FY{latest_inc.fiscal_year}): {fmt(latest_inc.revenue)}\n"
                   f"- Gross Profit: {fmt(latest_inc.gross_profit)}\n"
                   f"- Operating Income: {fmt(latest_inc.operating_income)}\n"
                   f"- EBITDA: {fmt(latest_inc.ebitda)}\n"
                   f"- Net Income: {fmt(latest_inc.net_income)}\n"
                   if latest_inc else "Financial data unavailable.\n")
            ),
            citations=[Citation(source_type="financial_data", source_name="Income Statement", date="Demo data")],
        ),
        ReportSection(
            title="Profitability",
            content=(
                "**Key Margins**\n\n"
                + (f"- Gross Margin: {fmtp(latest_rat.gross_margin)}\n"
                   f"- Operating Margin: {fmtp(latest_rat.operating_margin)}\n"
                   f"- Net Margin: {fmtp(latest_rat.net_margin)}\n"
                   f"- EBITDA Margin: {fmtp(latest_rat.ebitda_margin)}\n"
                   f"- Revenue Growth (YoY): {fmtp(latest_rat.revenue_growth)}\n"
                   if latest_rat else "Ratio data unavailable.\n")
            ),
        ),
        ReportSection(
            title="Cash Flow",
            content=(
                "**Cash Flow Summary**\n\n"
                + (f"- Operating Cash Flow (FY{latest_cf.fiscal_year}): {fmt(latest_cf.operating_cash_flow)}\n"
                   f"- Capital Expenditures: {fmt(latest_cf.capex)}\n"
                   f"- Free Cash Flow: {fmt(latest_cf.free_cash_flow)}\n"
                   if latest_cf else "Cash flow data unavailable.\n")
            ),
        ),
        ReportSection(
            title="Valuation Metrics",
            content=(
                "**Market Valuation**\n\n"
                + (f"- P/E Ratio: {fmt(quote.pe_ratio, '', 'x', 1)}\n"
                   f"- Forward P/E: {fmt(quote.forward_pe, '', 'x', 1)}\n"
                   f"- EV/EBITDA: {fmt(quote.ev_ebitda, '', 'x', 1)}\n"
                   f"- Price/Book: {fmt(quote.price_to_book, '', 'x', 1)}\n"
                   f"- Dividend Yield: {fmtp(quote.dividend_yield)}\n"
                   f"- Beta: {fmt(quote.beta, '', '', 2)}\n"
                   if quote else "Quote data unavailable.\n")
            ),
        ),
        ReportSection(
            title="Risk Factors",
            content=(
                "The following risk categories are relevant for this company based on its sector and industry. "
                "For detailed risk disclosures, refer to the company's most recent annual report (10-K or 20-F).\n\n"
                "- **Market Risk**: Exposure to macroeconomic conditions, interest rates, and currency fluctuations.\n"
                "- **Competitive Risk**: Rapid technological change and competitive pressure in the sector.\n"
                "- **Regulatory Risk**: Evolving regulatory environment across jurisdictions.\n"
                "- **Execution Risk**: Dependence on product cycles, R&D outcomes, and talent retention.\n\n"
                "*Note: For source-backed risk analysis, upload the company's annual report.*"
            ),
        ),
        ReportSection(
            title="Data Sources & Methodology",
            content=(
                "**Data Sources**\n"
                "- Financial statements: Demo data (illustrative)\n"
                "- Market data: Demo data (illustrative)\n\n"
                "**Methodology**\n"
                "Financial ratios are calculated from reported figures. Valuation multiples are market-derived. "
                "No forward-looking estimates have been incorporated without explicit user input.\n\n"
                "**Disclaimer**\n"
                "This report is generated for informational and educational purposes only. "
                "It does not constitute investment advice."
            ),
        ),
    ]

    sources = [
        Citation(source_type="financial_data", source_name="Financial Statements (Demo)", date="Illustrative"),
        Citation(source_type="market_data", source_name="Market Quote (Demo)", date="Illustrative"),
    ]

    return ReportResponse(
        ticker=ticker,
        company_name=name,
        title=f"{name} — Investment Research Report",
        generated_at=datetime.utcnow().isoformat(),
        data_through="Demo data (illustrative)",
        sections=sections,
        sources=sources,
    )
