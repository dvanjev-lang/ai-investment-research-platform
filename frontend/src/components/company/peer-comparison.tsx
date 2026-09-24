'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { formatCurrency, formatPercent, formatMultiple } from '@/lib/utils'
import { RefreshCw } from 'lucide-react'

interface Props { ticker: string }

export function PeerComparison({ ticker }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: ['peers', ticker],
    queryFn: () => api.getPeers(ticker),
  })

  if (isLoading) return (
    <div className="flex items-center justify-center h-40">
      <RefreshCw className="w-4 h-4 animate-spin text-muted-foreground" />
    </div>
  )

  const peers = data?.peers || []

  return (
    <div className="space-y-4">
      <div className="bg-card border border-border rounded-lg overflow-x-auto">
        <div className="px-4 py-3 border-b border-border">
          <h3 className="text-sm font-semibold">Peer Comparison</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Data presented neutrally. No company is ranked as better or worse.
          </p>
        </div>
        <table className="w-full financial-table">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left px-4 py-3">Company</th>
              <th className="text-right px-4 py-3">Market Cap</th>
              <th className="text-right px-4 py-3">P/E</th>
              <th className="text-right px-4 py-3">EV/EBITDA</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {peers.map((peer) => (
              <tr key={peer.ticker}>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-semibold text-sm text-primary">{peer.ticker}</span>
                    <span className="text-sm text-muted-foreground">{peer.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {formatCurrency(peer.market_cap)}
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {formatMultiple(peer.pe_ratio)}
                </td>
                <td className="px-4 py-3 text-right font-mono text-sm">
                  {formatMultiple(peer.ev_ebitda)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-muted-foreground">Demo data — illustrative only. No investment recommendation implied.</p>
    </div>
  )
}
