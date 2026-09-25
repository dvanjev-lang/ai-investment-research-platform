# AI Investment Research Platform

A full-stack investment research platform combining financial modeling,
AI-powered research, semantic document retrieval and agentic workflows.

The platform is designed as a technical portfolio project demonstrating
the intersection of Finance, AI Engineering, Data Engineering and
Full-Stack Development.

**[Live Demo](https://ai-investment-research-platform-one.vercel.app/dashboard)** — no installation required

---

## Overview

The platform allows users to research public companies through a single interface.

Users can:

- Search and analyze companies
- Explore financial statements
- Analyze financial ratios
- View historical price data
- Compare companies with peers
- Configure DCF valuations
- Run scenario and sensitivity analysis
- Upload financial documents
- Search documents semantically
- Ask AI-assisted research questions
- Generate structured research reports
- Inspect the research workflow and source citations

The system is designed for research and educational purposes and does
not provide personalized investment advice or buy/sell recommendations.

---

## Key Features

### Financial Analysis

- Multi-year financial statements
- Revenue and profitability analysis
- Financial ratios
- Dynamic company financial data
- DCF valuation
- Scenario analysis
- Sensitivity matrices
- EBIT and NOPAT calculations
- D&A integration

### AI Research

- OpenAI-powered research assistant
- Embedding-based semantic search
- Cosine similarity retrieval
- TF-IDF fallback
- Source-aware responses
- `[Data]` vs `[Analysis]` distinction
- Hallucination controls

### Agentic Research Workflow

The research workflow separates responsibilities across multiple specialized components:

1. Research Planner
2. Financial Data Agent
3. Document Research Agent
4. Risk Analysis Agent
5. Evidence Aggregator
6. Citation Validator
7. Research Writer

Each component performs actual research or analysis operations rather than representing a static UI trace.

### Document Intelligence

- PDF / TXT / DOCX ingestion
- Text extraction
- tiktoken chunking (512-token chunks, 64-token overlap)
- Embedding generation (`text-embedding-3-small`)
- Semantic retrieval via cosine similarity
- Context-aware, source-cited research

Uploaded documents are treated as untrusted content and are sanitized
before being passed into the model context.

### Security

- Prompt-injection sanitization (12 pattern classes)
- Untrusted document-content labeling in LLM context
- Pydantic v2 input validation
- 20 MB file size cap
- No frontend API secrets

### Testing

**97 automated tests** covering:

- DCF calculations and financial modeling
- API routes (all endpoints)
- RAG pipeline
- Embedding and retrieval logic
- Security sanitization
- Prompt-injection protection
- Validation
- Research workflows

---

## Architecture

```
                    ┌──────────────────────┐
                    │      Next.js UI      │
                    │  TypeScript / React  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI API     │
                    │        Python        │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      Financial Engine   Research Engine   Document Engine
             │                 │                 │
             │                 ▼                 ▼
             │         Agentic Workflow       Chunking
             │                 │             Embeddings
             │                 ▼             Retrieval
             │         Evidence Layer            │
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │      PostgreSQL      │
                    │  Financial + Vector  │
                    │         Data         │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      OpenAI API      │
                    │  LLM + Embeddings    │
                    └──────────────────────┘
```

### DCF Model

The valuation engine calculates:

```
EBIT  = EBITDA − D&A

NOPAT = EBIT × (1 − Tax Rate)

FCF   = NOPAT − CapEx − ΔNWC
```

The model supports:

- Base case
- Conservative case
- Optimistic case
- WACC sensitivity matrix
- Terminal growth sensitivity matrix

Pydantic validators enforce: WACC > TGR, spread ≥ 1%, D&A < EBITDA margin.
Invalid sensitivity cells return `null` rather than `0`.

### RAG Pipeline

Documents follow this pipeline:

```
Document
   ↓
Text Extraction (PDF / DOCX / TXT)
   ↓
Prompt-Injection Sanitization
   ↓
tiktoken Chunking (512 tokens, 64-token overlap)
   ↓
OpenAI text-embedding-3-small
   ↓
Vector Storage (numpy in-memory / pgvector in production)
   ↓
Cosine Similarity Search
   ↓
Top-k Relevant Chunks
   ↓
Research Workflow
   ↓
Source-Aware Response
```

A TF-IDF BM25 retrieval fallback is available when embedding
infrastructure is unavailable. The response includes a `retrieval_mode`
field (`"semantic"` or `"tfidf"`) so clients can display the retrieval
method accurately.

### Agentic Research

The research workflow separates responsibilities into independent stages:

```
User Question
      ↓
Research Planner
      ↓
┌──────────────┬───────────────┬───────────────┐
│  Financial   │  Document     │  Risk         │
│  Data Agent  │  Research     │  Analysis     │
└──────────────┴───────────────┴───────────────┘
                     ↓
              Evidence Aggregator
                     ↓
              Citation Validator
                     ↓
              Research Writer (GPT-4o)
                     ↓
               Final Response
```

Each stage performs real operations (API calls, semantic retrieval,
LLM synthesis) and is independently observable via the `agent_trace`
field in the API response.

---

## Technology Stack

**Frontend**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Recharts
- TanStack Query

**Backend**
- Python 3.11+
- FastAPI
- Pydantic v2

**Data**
- PostgreSQL
- SQLAlchemy (async)
- Alembic
- Financial data provider abstraction (mock / FMP / Alpha Vantage)

**AI**
- OpenAI GPT-4o
- OpenAI text-embedding-3-small
- tiktoken
- numpy (cosine similarity)

**Infrastructure**
- Docker Compose
- Vercel (frontend)
- Supabase / PostgreSQL
- AWS-oriented architecture (ECS/Fargate + S3)

---

## Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Company Analysis
![Company Analysis](docs/screenshots/company-analysis.png)

### DCF Valuation
![DCF Valuation](docs/screenshots/dcf-valuation.png)

### AI Research
![AI Research](docs/screenshots/ai-research.png)

### Document RAG
![Document RAG](docs/screenshots/document-rag.png)

---

## Running Locally

### Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# DATA_PROVIDER=mock works without any external APIs
# Set OPENAI_API_KEY to enable GPT-4o and real embeddings

uvicorn app.main:app --reload
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/api/docs`

### Frontend

```bash
cd frontend

npm install
npm run dev
```

App: `http://localhost:3000`

### Run tests

```bash
cd backend
pytest tests/ -v
# 97 tests, all passing
```

---

## Project Structure

```
ai-investment-research/
│
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route handlers
│   │   ├── data/          # Data provider abstraction + mock
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Document service (RAG + embeddings)
│   │   └── main.py
│   │
│   ├── tests/             # 97 tests
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # React components
│   │   └── lib/           # API client + types
│   └── package.json
│
├── database/              # Alembic migrations
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## Design Principles

**Accuracy over generated output**  
The system separates factual financial data from model-generated analysis.
Financial figures are sourced from the data layer, not hallucinated by the LLM.

**Evidence over unsupported claims**  
Research responses are built around retrieved data and source citations.
Every numerical claim is attributed to a specific source.

**Modular AI**  
Research responsibilities are separated into independently testable
and observable components.

**Security by design**  
Uploaded documents are treated as untrusted input and sanitized before
entering the model context.

**No investment recommendations**  
The platform is designed for research and analysis only. It explicitly
avoids buy/sell recommendations, target prices, and personalized investment advice.

---

## Disclaimer

This project is an educational and technical demonstration.

It does not constitute financial advice, investment advice,
recommendations, or an offer to buy or sell securities.

Financial calculations and AI-generated analysis should be independently
verified before being used for any real-world financial decision.

---

## Author

**Daniel van Jeveren**  
Finance × AI × Software Engineering
