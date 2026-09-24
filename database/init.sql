-- AI Investment Research Platform — Database Schema
-- Run this against a PostgreSQL instance to initialize the schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS vector;  -- enable in Supabase/prod for pgvector

-- Companies
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    exchange VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(150),
    description TEXT,
    headquarters VARCHAR(255),
    employees INTEGER,
    website VARCHAR(255),
    isin VARCHAR(20),
    currency VARCHAR(10) DEFAULT 'USD',
    extra_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);

-- Market data (OHLCV)
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    adjusted_close FLOAT,
    volume FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, date)
);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker_date ON market_data(ticker, date);

-- Financial statements
CREATE TABLE IF NOT EXISTS financial_statements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) NOT NULL,
    statement_type VARCHAR(30) NOT NULL,  -- income | balance | cashflow
    period VARCHAR(10) NOT NULL,           -- annual | quarterly
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    period_end VARCHAR(20),
    currency VARCHAR(10) DEFAULT 'USD',
    -- Income statement
    revenue FLOAT,
    cost_of_revenue FLOAT,
    gross_profit FLOAT,
    operating_expenses FLOAT,
    operating_income FLOAT,
    ebitda FLOAT,
    net_income FLOAT,
    eps FLOAT,
    eps_diluted FLOAT,
    shares_outstanding FLOAT,
    interest_expense FLOAT,
    income_tax FLOAT,
    depreciation_amortization FLOAT,
    -- Balance sheet
    cash FLOAT,
    short_term_investments FLOAT,
    total_current_assets FLOAT,
    total_assets FLOAT,
    total_current_liabilities FLOAT,
    total_liabilities FLOAT,
    total_equity FLOAT,
    total_debt FLOAT,
    net_debt FLOAT,
    -- Cash flow
    operating_cash_flow FLOAT,
    capex FLOAT,
    free_cash_flow FLOAT,
    financing_cash_flow FLOAT,
    investing_cash_flow FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_financials_ticker ON financial_statements(ticker, statement_type, period);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) NOT NULL,
    name VARCHAR(500),
    document_type VARCHAR(50),
    reporting_period VARCHAR(20),
    publication_date VARCHAR(20),
    source_url VARCHAR(1000),
    file_path VARCHAR(1000),
    page_count INTEGER,
    word_count INTEGER,
    is_processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_documents_ticker ON documents(ticker);

-- Document chunks (for RAG)
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    ticker VARCHAR(20),
    chunk_index INTEGER,
    content TEXT NOT NULL,
    page_number INTEGER,
    section VARCHAR(255),
    -- embedding vector(1536),  -- enable with pgvector
    embedding JSONB,            -- fallback: store as JSON array
    token_count INTEGER,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_ticker ON document_chunks(ticker);

-- Research queries (audit log)
CREATE TABLE IF NOT EXISTS research_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20),
    question TEXT NOT NULL,
    answer TEXT,
    citations JSONB,
    agent_trace JSONB,
    model_used VARCHAR(100),
    tokens_used INTEGER,
    latency_ms FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Research reports
CREATE TABLE IF NOT EXISTS research_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20),
    title VARCHAR(500),
    content JSONB,
    data_through VARCHAR(50),
    sources JSONB,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    model_used VARCHAR(100)
);

-- Watchlists
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Seed data: demo companies
INSERT INTO companies (ticker, name, exchange, sector, industry, currency, headquarters)
VALUES
    ('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'Technology', 'Semiconductors', 'USD', 'Santa Clara, CA'),
    ('MSFT', 'Microsoft Corporation', 'NASDAQ', 'Technology', 'Software—Infrastructure', 'USD', 'Redmond, WA'),
    ('AAPL', 'Apple Inc.', 'NASDAQ', 'Technology', 'Consumer Electronics', 'USD', 'Cupertino, CA'),
    ('AMZN', 'Amazon.com, Inc.', 'NASDAQ', 'Consumer Cyclical', 'Internet Retail', 'USD', 'Seattle, WA'),
    ('JPM', 'JPMorgan Chase & Co.', 'NYSE', 'Financial Services', 'Banks—Diversified', 'USD', 'New York, NY'),
    ('ASML', 'ASML Holding N.V.', 'NASDAQ', 'Technology', 'Semiconductor Equipment', 'EUR', 'Veldhoven, Netherlands'),
    ('BLK', 'BlackRock, Inc.', 'NYSE', 'Financial Services', 'Asset Management', 'USD', 'New York, NY'),
    ('AMD', 'Advanced Micro Devices, Inc.', 'NASDAQ', 'Technology', 'Semiconductors', 'USD', 'Santa Clara, CA')
ON CONFLICT (ticker) DO NOTHING;
