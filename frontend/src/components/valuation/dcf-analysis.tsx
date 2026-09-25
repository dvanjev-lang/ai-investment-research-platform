'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { api, DCFAssumptions } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import { TrendingUp, Loader2, Info, AlertCircle } from 'lucide-react'

interface Props { ticker: string }

const GENERIC_DEFAULTS: DCFAssumptions = {
  revenue_growth_rates: [0.10, 0.08, 0.07, 0.06, 0.05],
  ebitda_margin: 0.20,
  da_pct_revenue: 0.04,
  tax_rate: 0.21,
  capex_pct_revenue: 0.05,
  nwc_change_pct_revenue: 0.02,
  wacc: 0.10,
  terminal_growth_rate: 0.025,
  base_revenue: 1000,
}

export function DCFAnalysis({ ticker }: Props) {
  const [assumptions, setAssumptions] = useState<DCFAssumptions>(GENERIC_DEFAULTS)
  const [defaultsLoaded, setDefaultsLoaded] = useState(false)

  // Fetch company-specific defaults from the backend
  const { data: defaults, isLoading: loadingDefaults, isError: defaultsError } = useQuery({
    queryKey: ['dcf-defaults', ticker],
    queryFn: () => api.getDCFDefaults(ticker),
    staleTime: 5 * 60 * 1000,
  })

  // Apply fetched defaults once (don't overwrite user edits after that)
  useEffect(() => {
    if (defaults && !defaultsLoaded) {
      setAssumptions(defaults.defaults)
      setDefaultsLoaded(true)
    }
  }, [defaults, defaultsLoaded])

  const { mutate, data: dcf, isPending, isError: runError } = useMutation({
    mutationFn: () => api.runDCF(ticker, assumptions),
  })

  const update = (key: keyof DCFAssumptions, value: number) => {
    setAssumptions(prev => ({ ...prev, [key]: value }))
  }

  const fmtPct = (v: number) => `${(v * 100).toFixed(1)}%`

  return (
    <div className="space-y-4">
      <div className="bg-card border border-border rounded-lg p-5">
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold">DCF Analysis</h3>
          {loadingDefaults && (
            <span className="text-xs text-muted-foreground flex items-center gap-1 ml-auto">
              <Loader2 className="w-3 h-3 animate-spin" /> Loading company defaults…
            </span>
          )}
        </div>

        <div className="flex items-start gap-2 text-xs text-muted-foreground mb-4 bg-muted/50 px-3 py-2 rounded">
          <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <span>
            Illustrative scenario based on user-selected assumptions. Not a target price or investment recommendation.
            {defaults && (
              <span className="ml-1 opacity-70">
                Base revenue pre-filled from {defaults.data_note}.
              </span>
            )}
          </span>
        </div>

        {defaultsError && (
          <div className="flex items-center gap-2 text-xs text-destructive mb-3 bg-destructive/10 px-3 py-2 rounded">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            Could not load company defaults. Using generic assumptions.
          </div>
        )}

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-muted-foreground">
              Base Revenue ($M)
              {defaults && <span className="ml-1 text-primary">← from {defaults.data_note.split(' ').slice(0, 2).join(' ')}</span>}
            </label>
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
            <label className="text-xs text-muted-foreground">D&amp;A (% Revenue)</label>
            <input type="number" step="0.005" value={assumptions.da_pct_revenue}
              onChange={e => update('da_pct_revenue', +e.target.value)}
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
            <label className="text-xs text-muted-foreground">CapEx (% Revenue)</label>
            <input type="number" step="0.01" value={assumptions.capex_pct_revenue}
              onChange={e => update('capex_pct_revenue', +e.target.value)}
              className="w-full mt-1 bg-muted border border-border rounded px-3 py-1.5 text-sm font-mono outline-none focus:border-primary" />
          </div>
        </div>

        {runError && (
          <div className="flex items-center gap-2 text-xs text-destructive mt-3 bg-destructive/10 px-3 py-2 rounded">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            DCF failed. Check that WACC exceeds terminal growth rate by at least 1%, and D&amp;A &lt; EBITDA margin.
          </div>
        )}

        <button onClick={() => mutate()} disabled={isPending || loadingDefaults}
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
                <div className="text-xs text-muted-foreground mt-1">Enterprise Value ($M)</div>
                <div className="mt-3 pt-3 border-t border-border text-xs text-muted-foreground space-y-1">
                  <div className="flex justify-between">
                    <span>PV Terminal Value</span>
                    <span className="font-mono">{formatCurrency(scenario.pv_terminal_value)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>WACC</span>
                    <span className="font-mono">{fmtPct(scenario.assumptions.wacc)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>EBITDA Margin</span>
                    <span className="font-mono">{fmtPct(scenario.assumptions.ebitda_margin)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Year-by-year projections for base case */}
          {dcf.base_case.projections.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-5 overflow-x-auto">
              <h4 className="text-sm font-semibold mb-3">Base Case — Year-by-Year Projections ($M)</h4>
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border text-muted-foreground">
                    <th className="text-left px-2 py-2">Year</th>
                    <th className="text-right px-2 py-2">Revenue</th>
                    <th className="text-right px-2 py-2">EBITDA</th>
                    <th className="text-right px-2 py-2">EBIT</th>
                    <th className="text-right px-2 py-2">NOPAT</th>
                    <th className="text-right px-2 py-2">FCF</th>
                    <th className="text-right px-2 py-2">PV FCF</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {dcf.base_case.projections.map((yr) => (
                    <tr key={yr.year}>
                      <td className="px-2 py-2 font-mono">Y{yr.year}</td>
                      <td className="px-2 py-2 text-right font-mono">{formatCurrency(yr.revenue)}</td>
                      <td className="px-2 py-2 text-right font-mono">{formatCurrency(yr.ebitda)}</td>
                      <td className="px-2 py-2 text-right font-mono">{formatCurrency(yr.ebit)}</td>
                      <td className="px-2 py-2 text-right font-mono">{formatCurrency(yr.nopat)}</td>
                      <td className="px-2 py-2 text-right font-mono">{formatCurrency(yr.free_cash_flow)}</td>
                      <td className="px-2 py-2 text-right font-mono text-primary">{formatCurrency(yr.pv_fcf)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Sensitivity */}
          <div className="bg-card border border-border rounded-lg p-5 overflow-x-auto">
            <h4 className="text-sm font-semibold mb-3">Sensitivity: Enterprise Value ($M) — WACC vs Terminal Growth Rate</h4>
            <table className="financial-table">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left px-3 py-2 text-xs">WACC \ TGR</th>
                  {dcf.sensitivity.col_values.map(v => (
                    <th key={v} className="text-right px-3 py-2 text-xs">{fmtPct(v)}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {dcf.sensitivity.matrix.map((row, i) => (
                  <tr key={i}>
                    <td className="px-3 py-2 text-xs text-muted-foreground font-mono">
                      {fmtPct(dcf.sensitivity.row_values[i])}
                    </td>
                    {row.map((val, j) => (
                      <td key={j} className="px-3 py-2 text-right text-xs font-mono">
                        {val !== null ? formatCurrency(val) : <span className="text-muted-foreground">—</span>}
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
