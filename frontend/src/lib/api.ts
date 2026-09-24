import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

export const api = {
  searchCompanies: async (query: string) => {
    const { data } = await client.get(`/api/v1/companies/search`, { params: { q: query } })
    return data as CompanySearchResult[]
  },

  getCompanyProfile: async (ticker: string) => {
    const { data } = await client.get(`/api/v1/companies/${ticker}`)
    return data as CompanyProfile
  },

  getHistoricalPrices: async (ticker: string, period = '1y') => {
    const { data } = await client.get(`/api/v1/companies/${ticker}/prices`, { params: { period } })
    return data as { ticker: string; period: string; data: HistoricalPrice[] }
  },

  getFinancials: async (ticker: string, period = 'annual') => {
    const { data } = await client.get(`/api/v1/companies/${ticker}/financials`, { params: { period } })
    return data as FinancialsResponse
  },

  getPeers: async (ticker: string) => {
    const { data } = await client.get(`/api/v1/companies/${ticker}/peers`)
    return data as { ticker: string; peers: PeerCompany[] }
  },

  runDCF: async (ticker: string, assumptions: DCFAssumptions) => {
    const { data } = await client.post(`/api/v1/valuation/${ticker}/dcf`, assumptions)
    return data as DCFResponse
  },

  queryResearch: async (req: ResearchQueryRequest) => {
    const { data } = await client.post(`/api/v1/research/query`, req)
    return data as ResearchQueryResponse
  },

  generateReport: async (req: ReportRequest) => {
    const { data } = await client.post(`/api/v1/research/report`, req)
    return data as ReportResponse
  },

  uploadDocument: async (formData: FormData) => {
    const { data } = await client.post(`/api/v1/documents/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  listDocuments: async (ticker: string) => {
    const { data } = await client.get(`/api/v1/documents/${ticker}`)
    return data as { ticker: string; documents: Document[] }
  },
}

// Types (mirror backend schemas)
export interface CompanySearchResult {
  ticker: string
  name: string
  exchange?: string
  sector?: string
  industry?: string
  currency?: string
}

export interface CompanyBase {
  ticker: string
  name: string
  exchange?: string
  sector?: string
  industry?: string
  description?: string
  headquarters?: string
  employees?: number
  website?: string
  currency?: string
}

export interface QuoteData {
  ticker: string
  price?: number
  change?: number
  change_pct?: number
  market_cap?: number
  volume?: number
  high_52w?: number
  low_52w?: number
  pe_ratio?: number
  forward_pe?: number
  ev_ebitda?: number
  price_to_book?: number
  dividend_yield?: number
  beta?: number
  fetched_at?: string
  data_note?: string
}

export interface CompanyProfile {
  company: CompanyBase
  quote?: QuoteData
  data_as_of?: string
  data_provider: string
  disclaimer: string
}

export interface HistoricalPrice {
  date: string
  open?: number
  high?: number
  low?: number
  close?: number
  adjusted_close?: number
  volume?: number
}

export interface IncomeStatementRow {
  period: string
  fiscal_year?: number
  revenue?: number
  cost_of_revenue?: number
  gross_profit?: number
  operating_expenses?: number
  operating_income?: number
  ebitda?: number
  net_income?: number
  eps_diluted?: number
  shares_outstanding?: number
}

export interface BalanceSheetRow {
  period: string
  fiscal_year?: number
  cash?: number
  total_current_assets?: number
  total_assets?: number
  total_current_liabilities?: number
  total_liabilities?: number
  total_equity?: number
  total_debt?: number
  net_debt?: number
}

export interface CashFlowRow {
  period: string
  fiscal_year?: number
  operating_cash_flow?: number
  capex?: number
  free_cash_flow?: number
  financing_cash_flow?: number
  investing_cash_flow?: number
}

export interface FinancialRatios {
  ticker: string
  period?: string
  gross_margin?: number
  operating_margin?: number
  net_margin?: number
  ebitda_margin?: number
  roa?: number
  roe?: number
  roic?: number
  current_ratio?: number
  quick_ratio?: number
  debt_to_equity?: number
  debt_to_ebitda?: number
  interest_coverage?: number
  revenue_growth?: number
  ebitda_growth?: number
  fcf_growth?: number
}

export interface FinancialsResponse {
  ticker: string
  period_type: string
  income_statements: IncomeStatementRow[]
  balance_sheets: BalanceSheetRow[]
  cash_flows: CashFlowRow[]
  ratios: FinancialRatios[]
  currency: string
  data_note?: string
}

export interface PeerCompany {
  ticker: string
  name: string
  market_cap?: number
  revenue?: number
  gross_margin?: number
  operating_margin?: number
  pe_ratio?: number
  ev_ebitda?: number
  revenue_growth?: number
  roic?: number
}

export interface DCFAssumptions {
  revenue_growth_rates: number[]
  ebitda_margin: number
  tax_rate: number
  capex_pct_revenue: number
  nwc_change_pct_revenue: number
  wacc: number
  terminal_growth_rate: number
  base_revenue: number
}

export interface DCFScenario {
  name: string
  assumptions: DCFAssumptions
  projected_revenues: number[]
  projected_fcf: number[]
  terminal_value?: number
  enterprise_value?: number
  equity_value?: number
  implied_price?: number
}

export interface SensitivityMatrix {
  row_label: string
  col_label: string
  row_values: number[]
  col_values: number[]
  matrix: number[][]
}

export interface DCFResponse {
  ticker: string
  base_case: DCFScenario
  conservative_case: DCFScenario
  optimistic_case: DCFScenario
  sensitivity: SensitivityMatrix
  methodology_note: string
  generated_at?: string
}

export interface Citation {
  source_type: string
  source_name: string
  document_id?: string
  page_number?: number
  section?: string
  excerpt?: string
  date?: string
  url?: string
}

export interface AgentStep {
  agent: string
  action: string
  result_summary: string
  sources_consulted: string[]
}

export interface ResearchQueryRequest {
  ticker: string
  question: string
  include_documents?: boolean
  include_financial_data?: boolean
}

export interface ResearchQueryResponse {
  question: string
  answer: string
  citations: Citation[]
  agent_trace: AgentStep[]
  data_through?: string
  disclaimer: string
  confidence_note?: string
}

export interface ReportRequest {
  ticker: string
  include_dcf?: boolean
  include_peers?: boolean
}

export interface ReportSection {
  title: string
  content: string
  citations: Citation[]
}

export interface ReportResponse {
  ticker: string
  company_name: string
  title: string
  generated_at: string
  data_through: string
  sections: ReportSection[]
  sources: Citation[]
  disclaimer: string
}

export interface Document {
  id: string
  ticker: string
  name: string
  document_type: string
  reporting_period?: string
  word_count?: number
  is_processed: boolean
}
