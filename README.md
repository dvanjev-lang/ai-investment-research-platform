# AI Investment Research Platform

A full-stack AI-powered investment research platform combining Python, FastAPI, Next.js, PostgreSQL, OpenAI, and RAG to analyze public-company financial data and source-backed corporate disclosures.

> **Disclaimer:** This platform provides informational and analytical content for educational and research purposes only. It does not constitute investment advice, a recommendation to buy or sell any security, or a guarantee of future performance.

---

## Overview

This portfolio project demonstrates integration of:

- **Financial Analytics** — Income statements, balance sheets, cash flows, financial ratios, and valuation metrics
- **AI/LLM Research** — GPT-4o–powered research assistant with structured outputs and source citations
- **RAG Architecture** — Document upload → text extraction → chunking → embeddings → vector retrieval → cited answers
- **Agentic Workflows** — Research Planner → Financial Data Agent → Document Researcher → Citation Validator pipeline
- **DCF Valuation** — Configurable 3-scenario DCF with sensitivity analysis
- **Professional UI** — Institutional-grade dark/light mode dashboard built with Next.js 14 + Tailwind + Recharts

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, React, Tailwind CSS, Recharts |
| Backend | Python 3.11+, FastAPI, Pydantic |
| Database | PostgreSQL (Supabase), SQLAlchemy, Alembic |
| AI | OpenAI GPT-4o, text-embedding-3-small |
| Vector DB | pgvector (PostgreSQL extension) |
| Cloud | AWS-oriented (ECS/Fargate + S3 + CloudWatch) |
| Deployment | Vercel (frontend), Docker (backend) |

---

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (or Supabase account)
- OpenAI API key (optional for demo mode)

### 1. Clone and setup

```bash
git clone https://github.com/yourusername/ai-investment-research.git
cd ai-investment-research
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — set DATABASE_URL, OPENAI_API_KEY
# DATA_PROVIDER=mock works without any API key

uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/api/docs

### 3. Frontend

```bash
cd frontend
npm install

cp .env.local.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

App: http://localhost:3000

### 4. Demo mode

Set `DATA_PROVIDER=mock` in `.env` to run entirely on demo data — no external APIs needed. The platform shows realistic financial data for NVIDIA, Microsoft, Apple, Amazon, JPMorgan, ASML, BlackRock, and AMD.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API key (GPT-4o + embeddings) | Optional |
| `DATA_PROVIDER` | `mock` / `fmp` / `alpha_vantage` | Yes |
| `FMP_API_KEY` | Financial Modeling Prep API key | If using FMP |
| `APP_SECRET_KEY` | JWT secret key | Yes (prod) |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│  Dashboard │ Company │ Research │ Valuation │ Documents  │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│  /companies  /research  /valuation  /documents          │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Data Provider│  │  AI/RAG      │  │  DCF Engine   │  │
│  │ (Mock/FMP)   │  │  Pipeline    │  │  (3 scenarios)│  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  PostgreSQL / Supabase                   │
│   companies │ financial_statements │ documents           │
│   document_chunks (pgvector) │ research_reports          │
└─────────────────────────────────────────────────────────┘
```

---

## Features

### Financial Analytics
- Multi-year income statements, balance sheets, cash flow statements
- 15+ financial ratios (profitability, liquidity, leverage, efficiency, growth)
- Interactive price charts with 1m/3m/6m/1y/3y/5y periods
- Peer comparison tables

### AI Research
- GPT-4o–powered research assistant
- Source-cited answers with agent trace visibility
- Structured research report generation (15 sections)
- Document upload and RAG-based retrieval

### Valuation
- DCF analysis with configurable assumptions
- Base / Conservative / Optimistic scenarios
- WACC × Terminal Growth Rate sensitivity matrix

### UI/UX
- Institutional-grade dark/light mode
- Responsive design
- Persistent disclaimer on all pages
- No buy/sell recommendations anywhere

---

## Data Sources

In demo mode: static illustrative data (clearly labeled).

For live data, implement `FinancialDataProvider` for:
- [Financial Modeling Prep](https://financialmodelingprep.com/) — comprehensive fundamentals
- [Alpha Vantage](https://www.alphavantage.co/) — market data
- [Polygon.io](https://polygon.io/) — real-time + historical prices

---

## Limitations

- Demo data is static and illustrative, not sourced from live feeds
- RAG pipeline uses simple keyword search in demo mode; production should use pgvector embeddings
- No authentication in current version (add JWT + Supabase Auth for production)
- DCF terminal value assumes perpetuity (Gordon Growth Model)
- No real-time data streaming

---

## Roadmap

- [ ] Live data provider (FMP or Polygon)
- [ ] pgvector embeddings for semantic document search
- [ ] Authentication (Supabase Auth + JWT)
- [ ] AWS deployment (ECS/Fargate + S3 + CloudWatch)
- [ ] Watchlist and saved companies
- [ ] Export to PDF
- [ ] More companies (500+ tickers)

---

## Compliance Note

This platform is built as a portfolio / educational project. It explicitly avoids providing:
- Buy/sell recommendations
- Target prices
- Personalized investment advice
- Guaranteed return scenarios

All scenario analyses are clearly labeled as illustrative assumptions.

---

*Built to demonstrate financial analytics, AI engineering, and full-stack development capabilities.*
