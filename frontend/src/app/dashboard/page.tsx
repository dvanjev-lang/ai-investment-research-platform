'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Search, TrendingUp, FileText, BarChart3, Brain, Building2 } from 'lucide-react'
import { CompanySearch } from '@/components/search/company-search'
import { Disclaimer } from '@/components/ui/disclaimer'

const FEATURED_COMPANIES = [
  { ticker: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology', change: '+1.45%', positive: true },
  { ticker: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology', change: '+0.53%', positive: true },
  { ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology', change: '-0.68%', positive: false },
  { ticker: 'AMZN', name: 'Amazon.com', sector: 'Consumer', change: '+1.79%', positive: true },
  { ticker: 'JPM', name: 'JPMorgan Chase', sector: 'Financial Services', change: '+0.45%', positive: true },
  { ticker: 'ASML', name: 'ASML Holding', sector: 'Technology', change: '-0.60%', positive: false },
]

const CAPABILITIES = [
  {
    icon: BarChart3,
    title: 'Financial Analytics',
    description: 'Income statements, balance sheets, cash flows, and financial ratios across 5+ years.',
  },
  {
    icon: Brain,
    title: 'AI Research Assistant',
    description: 'Ask questions about any company. AI retrieves answers from financial data and uploaded documents.',
  },
  {
    icon: TrendingUp,
    title: 'Valuation Models',
    description: 'DCF analysis with configurable assumptions and sensitivity matrices.',
  },
  {
    icon: FileText,
    title: 'Document Intelligence',
    description: 'Upload annual reports and earnings presentations. AI extracts and cites key information.',
  },
  {
    icon: Building2,
    title: 'Peer Comparison',
    description: 'Compare revenue growth, margins, and valuation multiples across industry peers.',
  },
]

export default function DashboardPage() {
  const router = useRouter()

  const handleCompanySelect = (ticker: string) => {
    router.push(`/company/${ticker}`)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 bg-primary rounded flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-semibold text-sm tracking-tight">AI Investment Research</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
            <a href="/dashboard" className="text-foreground font-medium">Dashboard</a>
            <span className="text-border">|</span>
            <span className="text-xs bg-muted px-2 py-0.5 rounded text-muted-foreground">Research only — not investment advice</span>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary text-xs font-medium px-3 py-1.5 rounded-full">
            <Brain className="w-3.5 h-3.5" />
            AI-Powered Financial Research
          </div>
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-foreground">
            Investment Research Platform
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg leading-relaxed">
            Analyze public companies with structured financial data, AI-assisted research,
            and source-cited document analysis.
          </p>
        </div>

        {/* Search */}
        <div className="max-w-2xl mx-auto mb-12">
          <CompanySearch onSelect={handleCompanySelect} />
        </div>

        {/* Featured companies */}
        <section className="mb-12">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-4">
            Available Companies (Demo)
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {FEATURED_COMPANIES.map((co) => (
              <button
                key={co.ticker}
                onClick={() => handleCompanySelect(co.ticker)}
                className="group p-4 bg-card border border-border rounded-lg text-left hover:border-primary/50 hover:bg-primary/5 transition-all duration-150"
              >
                <div className="font-mono font-semibold text-sm text-foreground group-hover:text-primary transition-colors">
                  {co.ticker}
                </div>
                <div className="text-xs text-muted-foreground mt-0.5 truncate">{co.name}</div>
                <div className={`text-xs font-medium mt-2 ${co.positive ? 'text-positive' : 'text-negative'}`}>
                  {co.change}
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Capabilities */}
        <section className="mb-12">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-4">
            Platform Capabilities
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {CAPABILITIES.map((cap) => (
              <div key={cap.title} className="p-5 bg-card border border-border rounded-lg">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center">
                    <cap.icon className="w-4 h-4 text-primary" />
                  </div>
                  <h3 className="font-medium text-sm">{cap.title}</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{cap.description}</p>
              </div>
            ))}
          </div>
        </section>

        <Disclaimer />
      </main>
    </div>
  )
}
