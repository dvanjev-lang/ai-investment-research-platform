'use client'

import { CompanyProfile } from '@/lib/api'
import { formatCurrency, formatPercent, changeColor } from '@/lib/utils'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface CompanyHeaderProps {
  profile: CompanyProfile
}

export function CompanyHeader({ profile }: CompanyHeaderProps) {
  const { company, quote } = profile

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        {/* Left: Company identity */}
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-semibold tracking-tight">{company.name}</h1>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="font-mono font-semibold text-foreground">{company.ticker}</span>
            {company.exchange && <span>· {company.exchange}</span>}
            {company.sector && <span>· {company.sector}</span>}
          </div>
        </div>

        {/* Right: Price */}
        {quote && (
          <div className="text-right">
            <div className="text-3xl font-mono font-semibold">
              {quote.price ? `$${quote.price.toFixed(2)}` : '—'}
            </div>
            <div className={`flex items-center justify-end gap-1 text-sm font-medium mt-0.5 ${changeColor(quote.change_pct)}`}>
              {quote.change_pct && quote.change_pct > 0 ? (
                <TrendingUp className="w-3.5 h-3.5" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5" />
              )}
              {quote.change ? `${quote.change > 0 ? '+' : ''}${quote.change.toFixed(2)}` : ''}
              {quote.change_pct ? ` (${quote.change_pct > 0 ? '+' : ''}${quote.change_pct.toFixed(2)}%)` : ''}
            </div>
            {quote.data_note && (
              <div className="text-xs text-muted-foreground mt-1">{quote.data_note}</div>
            )}
          </div>
        )}
      </div>

      {/* Key stats row */}
      {quote && (
        <div className="mt-5 pt-5 border-t border-border grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            { label: 'Market Cap', value: formatCurrency(quote.market_cap) },
            { label: '52W High', value: quote.high_52w ? `$${quote.high_52w.toFixed(2)}` : '—' },
            { label: '52W Low', value: quote.low_52w ? `$${quote.low_52w.toFixed(2)}` : '—' },
            { label: 'P/E Ratio', value: quote.pe_ratio ? `${quote.pe_ratio.toFixed(1)}x` : '—' },
            { label: 'EV/EBITDA', value: quote.ev_ebitda ? `${quote.ev_ebitda.toFixed(1)}x` : '—' },
            { label: 'Dividend Yield', value: quote.dividend_yield ? formatPercent(quote.dividend_yield) : '—' },
          ].map(({ label, value }) => (
            <div key={label}>
              <div className="text-xs text-muted-foreground">{label}</div>
              <div className="text-sm font-mono font-medium mt-0.5">{value}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
