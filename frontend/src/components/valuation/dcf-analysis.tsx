'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api, DCFAssumptions } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import { TrendingUp, Loader2, Info } from 'lucide-react'

interface Props { ticker: string }

const DEFAULT_ASSUMPTIONS: DCFAssumptions = {
  revenue_growth_rates: [0.15, 0.12, 0.10, 0.08, 0.06],
  ebitda_margin: 0.25,
  tax_rate: 0.21,
  capex_pct_revenue: 0.05,
  nwc_change_pct_revenue: 0.02,
  wacc: 0.10,
  terminal_growth_rate: 0.025,
  base_revenue: 60922,
}

export function DCFAnalysis({ ticker }: Props) {
  const [assumptions, setAssumptions] = useState<DCFAssumptions>(DEFAULT_ASSUMPTIONS)

  const { mutate, data: dcf, isPending } = useMutation({
    mutationFn: () => api.runDCF(ticker, assumptions),
  })

  const update = (key: keyof DCFAssumptions, value: number) => {
    setAssumptions(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="space-y-4">
      <div className="bg-card border border-border rounded-lg p-5">
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold">DCF Analysis</h3>
        </div>
        <div className="flex items-start gap-2 text-xs text-muted-foreground mb-4 bg-muted/50 px-3 py-2 rounded">
          <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          Illustrative scenario based on user-selected assumptions. Not a target price or investment recommendation.
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-muted-foreground">Base Revenue ($M)</label>
            <input type="number" value={assumptions.base_revenue}
              onChange={e => update('base_revenue', +e.target.value)}
              className="w-full mt-1 bg-muted border border-border rounded px-3 py-1.5 text-sm font-mono outline-none focus:border-primary" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground">EBITDA Margin</label>
            <input type="number" step="0.01" value={assumptions.ebitda_margin}
              onChange={e => update('ebitda_margin', +e.target.value)}
              className="w-full mt-1 bg-muted border border-border rounded px-3 py-1.5 text-sm font-mono outline-none focus:border-primary" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground">WACC</label>
            <input type="number" step="0.01" value={assumptions.wacc}
              onChange={e => update('wacc', +e.target.value)}
              className="w-full mt-1 bg-muted border border-border rounded px-3 py-1.5 text-sm font-mono outline-none focus:border-primary" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground">Terminal Growth Rate</label>
            <input type="number" step="0.005" value={assumptions.terminal_growth_rate}
              onChange={e => update('terminal_growth_rate', +e.target.value)}
              className="w-full mt-1 bg-muted border border-border rounded px-3 py-1.5 text-sm font-mono outline-none focus:border-primary" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground">Tax Rate</label>
            <input type="number" step="0.01" value={assumptions.tax_rate}
              onChange={e => update('tax_rate', +e.target.value)}
              className="w-full mt-1 bg-muted border border-border rounded px-3 py-1.5 text-sm font-mono outline-none focus:border-primary" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground">CapEx (% Rev)</label>
            <input type="number" step="0.01" value={assumptions.capex_pct_revenue}
              onChange={e => update('capex_pct_revenue', +e.target.value)}
              className="w-full mt-1 bg-muted border border-border rounded px-3 py-1.5 text-sm font-mono outline-none focus:border-primary" />
          </div>
        </div>

        <button onClick={() => mutate()} disabled={isPending}
          className="mt-4 flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors">
          {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <TrendingUp className="w-4 h-4" />}
          Run DCF Analysis
        </button>
      </div>

      {dcf && (
        <div className="space-y-4">
          {/* Scenarios */}
          <div className="grid md:grid-cols-3 gap-4">
            {[dcf.conservative_case, dcf.base_case, dcf.optimistic_case].map((scenario) => (
              <div key={scenario.name} className="bg-card border border-border rounded-lg p-4">
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                  {scenario.name}
                </div>
                <div className="text-2xl font-mono font-semibold">
                  {formatCurrency(scenario.enterprise_value)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">Enterprise Value</div>
                <div className="mt-3 pt-3 border-t border-border text-xs text-muted-foreground space-y-1">
                  <div className="flex justify-between">
                    <span>Terminal Value</span>
                    <span className="font-mono">{formatCurrency(scenario.terminal_value)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>WACC</span>
                    <span className="font-mono">{(scenario.assumptions.wacc * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Sensitivity */}
          <div className="bg-card border border-border rounded-lg p-5 overflow-x-auto">
            <h4 className="text-sm font-semibold mb-3">Sensitivity: Enterprise Value ($M) — WACC vs Terminal Growth Rate</h4>
            <table className="financial-table">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left px-3 py-2 text-xs">WACC \ TGR</th>
                  {dcf.sensitivity.col_values.map(v => (
                    <th key={v} className="text-right px-3 py-2 text-xs">{(v * 100).toFixed(1)}%</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {dcf.sensitivity.matrix.map((row, i) => (
                  <tr key={i}>
                    <td className="px-3 py-2 text-xs text-muted-foreground font-mono">
                      {(dcf.sensitivity.row_values[i] * 100).toFixed(1)}%
                    </td>
                    {row.map((val, j) => (
                      <td key={j} className="px-3 py-2 text-right text-xs font-mono">
                        {formatCurrency(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="text-xs text-muted-foreground">{dcf.methodology_note}</p>
        </div>
      )}
    </div>
  )
}
