'use client'

import { useState, useCallback } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { api, CompanySearchResult } from '@/lib/api'

interface CompanySearchProps {
  onSelect: (ticker: string) => void
}

export function CompanySearch({ onSelect }: CompanySearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<CompanySearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)

  const search = useCallback(async (q: string) => {
    if (q.length < 1) { setResults([]); setOpen(false); return }
    setLoading(true)
    try {
      const data = await api.searchCompanies(q)
      setResults(data)
      setOpen(true)
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const q = e.target.value
    setQuery(q)
    const timer = setTimeout(() => search(q), 300)
    return () => clearTimeout(timer)
  }

  return (
    <div className="relative">
      <div className="flex items-center gap-3 bg-card border border-border rounded-lg px-4 py-3 focus-within:border-primary transition-colors">
        {loading ? (
          <Loader2 className="w-4 h-4 text-muted-foreground animate-spin shrink-0" />
        ) : (
          <Search className="w-4 h-4 text-muted-foreground shrink-0" />
        )}
        <input
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => query.length > 0 && setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder="Search by company name or ticker (e.g. NVIDIA, MSFT, ASML)"
          className="flex-1 bg-transparent text-sm placeholder:text-muted-foreground outline-none"
        />
      </div>

      {open && results.length > 0 && (
        <div className="absolute z-50 top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg overflow-hidden">
          {results.map((r) => (
            <button
              key={r.ticker}
              onMouseDown={() => { onSelect(r.ticker); setOpen(false); setQuery('') }}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-muted/50 transition-colors text-left border-b border-border/50 last:border-0"
            >
              <span className="font-mono font-semibold text-sm w-14 text-primary">{r.ticker}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{r.name}</div>
                <div className="text-xs text-muted-foreground">{r.exchange} · {r.sector}</div>
              </div>
            </button>
          ))}
        </div>
      )}

      {open && query.length > 0 && results.length === 0 && !loading && (
        <div className="absolute z-50 top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg px-4 py-3 text-sm text-muted-foreground">
          No results for &quot;{query}&quot;. Try NVDA, MSFT, AAPL, AMZN, JPM, ASML.
        </div>
      )}
    </div>
  )
}
