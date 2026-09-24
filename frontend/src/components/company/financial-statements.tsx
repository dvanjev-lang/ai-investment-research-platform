'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { formatCurrency, formatPercent } from '@/lib/utils'
import { RefreshCw } from 'lucide-react'

interface Props { ticker: string }

export function FinancialStatements({ ticker }: Props) {
  const [period, setPeriod] = useState<'annual' | 'quarterly'>('annual')
  const [activeStatement, setActiveStatement] = useState<'income' | 'balance' | 'cashflow' | 'ratios'>('income')

  const { data, isLoading } = useQuery({
    queryKey: ['financials', ticker, period],
    queryFn: () => api.getFinancials(ticker, period),
  })

  if (isLoading) return (
    <div className="flex items-center justify-center h-40">
      <RefreshCw className="w-4 h-4 animate-spin text-muted-foreground" />
    </div>
  )

  const income = data?.income_statements || []
  const balance = data?.balance_sheets || []
  const cashflow = data?.cash_flows || []
  const ratios = data?.ratios || []

  const years = income.map(r => `FY${r.fiscal_year}`)

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex gap-2 flex-wrap">
        <div className="flex gap-1 bg-muted p-1 rounded-lg">
          {(['annual', 'quarterly'] as const).map(p => (
            <button key={p} onClick={() => setPeriod(p)}
              className={`px-3 py-1.5 text-xs font-medium rounded transition-colors capitalize ${
                period === p ? 'bg-card shadow-sm text-foreground' : 'text-muted-foreground'
              }`}>
              {p}
            </button>
          ))}
        </div>
        <div className="flex gap-1 bg-muted p-1 rounded-lg">
          {([['income', 'Income Statement'], ['balance', 'Balance Sheet'], ['cashflow', 'Cash Flow'], ['ratios', 'Ratios']] as const).map(([id, label]) => (
            <button key={id} onClick={() => setActiveStatement(id)}
              className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                activeStatement === id ? 'bg-card shadow-sm text-foreground' : 'text-muted-foreground'
              }`}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tables */}
      <div className="bg-card border border-border rounded-lg overflow-x-auto">
        <table className="w-full financial-table">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left px-4 py-3 min-w-[200px]">Metric</th>
              {years.map(y => <th key={y} className="text-right px-4 py-3">{y}</th>)}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {activeStatement === 'income' && income.length > 0 && [
              { label: 'Revenue', key: 'revenue' as const, format: formatCurrency },
              { label: 'Cost of Revenue', key: 'cost_of_revenue' as const, format: formatCurrency },
              { label: 'Gross Profit', key: 'gross_profit' as const, format: formatCurrency },
              { label: 'Operating Expenses', key: 'operating_expenses' as const, format: formatCurrency },
              { label: 'Operating Income', key: 'operating_income' as const, format: formatCurrency },
              { label: 'EBITDA', key: 'ebitda' as const, format: formatCurrency },
              { label: 'Net Income', key: 'net_income' as const, format: formatCurrency },
              { label: 'EPS (Diluted)', key: 'eps_diluted' as const, format: (v: number) => v ? `$${v.toFixed(2)}` : '—' },
            ].map(row => (
              <tr key={row.label}>
                <td className="px-4 py-2.5 text-sm text-muted-foreground">{row.label}</td>
                {income.map((r, i) => (
                  <td key={i} className="px-4 py-2.5 text-right text-sm font-mono">
                    {r[row.key] !== undefined ? row.format(r[row.key] as number) : '—'}
                  </td>
                ))}
              </tr>
            ))}

            {activeStatement === 'balance' && balance.length > 0 && [
              { label: 'Cash & Equivalents', key: 'cash' as const },
              { label: 'Current Assets', key: 'total_current_assets' as const },
              { label: 'Total Assets', key: 'total_assets' as const },
              { label: 'Current Liabilities', key: 'total_current_liabilities' as const },
              { label: 'Total Liabilities', key: 'total_liabilities' as const },
              { label: 'Total Equity', key: 'total_equity' as const },
              { label: 'Total Debt', key: 'total_debt' as const },
              { label: 'Net Debt', key: 'net_debt' as const },
            ].map(row => (
              <tr key={row.label}>
                <td className="px-4 py-2.5 text-sm text-muted-foreground">{row.label}</td>
                {balance.map((r, i) => (
                  <td key={i} className="px-4 py-2.5 text-right text-sm font-mono">
                    {formatCurrency(r[row.key])}
                  </td>
                ))}
              </tr>
            ))}

            {activeStatement === 'cashflow' && cashflow.length > 0 && [
              { label: 'Operating Cash Flow', key: 'operating_cash_flow' as const },
              { label: 'Capital Expenditures', key: 'capex' as const },
              { label: 'Free Cash Flow', key: 'free_cash_flow' as const },
              { label: 'Investing Cash Flow', key: 'investing_cash_flow' as const },
              { label: 'Financing Cash Flow', key: 'financing_cash_flow' as const },
            ].map(row => (
              <tr key={row.label}>
                <td className="px-4 py-2.5 text-sm text-muted-foreground">{row.label}</td>
                {cashflow.map((r, i) => (
                  <td key={i} className="px-4 py-2.5 text-right text-sm font-mono">
                    {formatCurrency(r[row.key])}
                  </td>
                ))}
              </tr>
            ))}

            {activeStatement === 'ratios' && ratios.length > 0 && [
              { label: 'Gross Margin', key: 'gross_margin' as const, format: formatPercent },
              { label: 'Operating Margin', key: 'operating_margin' as const, format: formatPercent },
              { label: 'Net Margin', key: 'net_margin' as const, format: formatPercent },
              { label: 'EBITDA Margin', key: 'ebitda_margin' as const, format: formatPercent },
              { label: 'ROA', key: 'roa' as const, format: formatPercent },
              { label: 'ROE', key: 'roe' as const, format: formatPercent },
              { label: 'Current Ratio', key: 'current_ratio' as const, format: (v: number) => v ? `${v.toFixed(2)}x` : '—' },
              { label: 'Debt/Equity', key: 'debt_to_equity' as const, format: (v: number) => v ? `${v.toFixed(2)}x` : '—' },
              { label: 'Revenue Growth (YoY)', key: 'revenue_growth' as const, format: formatPercent },
            ].map(row => (
              <tr key={row.label}>
                <td className="px-4 py-2.5 text-sm text-muted-foreground">{row.label}</td>
                {ratios.map((r, i) => (
                  <td key={i} className="px-4 py-2.5 text-right text-sm font-mono">
                    {r[row.key] !== undefined ? row.format(r[row.key] as number) : '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {data?.data_note && (
          <div className="px-4 py-2 border-t border-border text-xs text-muted-foreground">
            {data.data_note}
          </div>
        )}
      </div>
    </div>
  )
}
