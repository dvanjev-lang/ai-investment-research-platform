'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, TrendingUp, FileText, BarChart3, Brain, Users, Building2, RefreshCw } from 'lucide-react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { CompanyHeader } from '@/components/company/company-header'
import { FinancialStatements } from '@/components/company/financial-statements'
import { PriceChart } from '@/components/company/price-chart'
import { ResearchAssistant } from '@/components/research/research-assistant'
import { ReportGenerator } from '@/components/research/report-generator'
import { PeerComparison } from '@/components/company/peer-comparison'
import { DocumentUpload } from '@/components/documents/document-upload'
import { DCFAnalysis } from '@/components/valuation/dcf-analysis'
import { Disclaimer } from '@/components/ui/disclaimer'

const TABS = [
  { id: 'overview', label: 'Overview', icon: Building2 },
  { id: 'financials', label: 'Financials', icon: BarChart3 },
  { id: 'valuation', label: 'Valuation', icon: TrendingUp },
  { id: 'peers', label: 'Peer Comparison', icon: Users },
  { id: 'research', label: 'AI Research', icon: Brain },
  { id: 'documents', label: 'Documents', icon: FileText },
]

export default function CompanyPage() {
  const params = useParams()
  const ticker = (params.ticker as string).toUpperCase()
  const [activeTab, setActiveTab] = useState('overview')

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['company', ticker],
    queryFn: () => api.getCompanyProfile(ticker),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center gap-3 text-muted-foreground">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span className="text-sm">Loading {ticker}...</span>
        </div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-3">
          <p className="text-muted-foreground">Could not load data for {ticker}</p>
          <Link href="/dashboard" className="text-sm text-primary hover:underline">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header nav */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Dashboard
            </Link>
            <span className="text-border">|</span>
            <span className="font-mono font-semibold text-sm">{ticker}</span>
            <span className="text-sm text-muted-foreground hidden md:block">
              {profile.company.name}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Company header / key stats */}
        <CompanyHeader profile={profile} />

        {/* Tab navigation */}
        <nav className="flex gap-1 border-b border-border overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-all whitespace-nowrap -mb-px ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <tab.icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Tab content */}
        <div>
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <PriceChart ticker={ticker} />
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-card border border-border rounded-lg p-5">
                  <h3 className="text-sm font-semibold mb-3">About</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {profile.company.description || 'No description available.'}
                  </p>
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    {[
                      { label: 'Sector', value: profile.company.sector },
                      { label: 'Industry', value: profile.company.industry },
                      { label: 'Exchange', value: profile.company.exchange },
                      { label: 'Headquarters', value: profile.company.headquarters },
                      { label: 'Employees', value: profile.company.employees?.toLocaleString() },
                      { label: 'Currency', value: profile.company.currency },
                    ].map(({ label, value }) => value && (
                      <div key={label}>
                        <div className="text-xs text-muted-foreground">{label}</div>
                        <div className="text-sm font-medium mt-0.5">{value}</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-card border border-border rounded-lg p-5">
                  <h3 className="text-sm font-semibold mb-3">Valuation Snapshot</h3>
                  {profile.quote && (
                    <div className="space-y-2">
                      {[
                        { label: 'P/E Ratio', value: profile.quote.pe_ratio?.toFixed(1) + 'x' },
                        { label: 'Forward P/E', value: profile.quote.forward_pe?.toFixed(1) + 'x' },
                        { label: 'EV/EBITDA', value: profile.quote.ev_ebitda?.toFixed(1) + 'x' },
                        { label: 'Price/Book', value: profile.quote.price_to_book?.toFixed(1) + 'x' },
                        { label: 'Dividend Yield', value: profile.quote.dividend_yield ? (profile.quote.dividend_yield * 100).toFixed(2) + '%' : '—' },
                        { label: 'Beta', value: profile.quote.beta?.toFixed(2) },
                      ].map(({ label, value }) => (
                        <div key={label} className="flex justify-between text-sm py-1 border-b border-border/50 last:border-0">
                          <span className="text-muted-foreground">{label}</span>
                          <span className="font-mono font-medium">{value || '—'}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {profile.data_as_of && (
                    <p className="text-xs text-muted-foreground mt-3">Data as of: {profile.data_as_of}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'financials' && <FinancialStatements ticker={ticker} />}
          {activeTab === 'valuation' && (
            <div className="space-y-6">
              <DCFAnalysis ticker={ticker} />
            </div>
          )}
          {activeTab === 'peers' && <PeerComparison ticker={ticker} />}
          {activeTab === 'research' && (
            <div className="space-y-6">
              <ResearchAssistant ticker={ticker} />
              <ReportGenerator ticker={ticker} />
            </div>
          )}
          {activeTab === 'documents' && <DocumentUpload ticker={ticker} />}
        </div>

        <Disclaimer />
      </main>
    </div>
  )
}
