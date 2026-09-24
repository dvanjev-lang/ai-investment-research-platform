'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '@/lib/api'
import { RefreshCw } from 'lucide-react'

const PERIODS = ['1m', '3m', '6m', '1y', '3y', '5y'] as const

interface PriceChartProps { ticker: string }

export function PriceChart({ ticker }: PriceChartProps) {
  const [period, setPeriod] = useState<string>('1y')

  const { data, isLoading } = useQuery({
    queryKey: ['prices', ticker, period],
    queryFn: () => api.getHistoricalPrices(ticker, period),
  })

  const prices = data?.data || []
  const firstPrice = prices[0]?.close || 0
  const lastPrice = prices[prices.length - 1]?.close || 0
  const isPositive = lastPrice >= firstPrice
  const chartColor = isPositive ? 'hsl(142, 71%, 45%)' : 'hsl(0, 72%, 51%)'

  return (
    <div className="bg-card border border-border rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold">Price History</h3>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
                period === p
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              }`}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="h-48 flex items-center justify-center">
          <RefreshCw className="w-4 h-4 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={prices} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={chartColor} stopOpacity={0.2} />
                <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10, fill: 'hsl(215,16%,47%)' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => v.slice(5)}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 10, fill: 'hsl(215,16%,47%)' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `$${v.toFixed(0)}`}
              width={55}
            />
            <Tooltip
              contentStyle={{
                background: 'hsl(222,47%,9%)',
                border: '1px solid hsl(222,47%,15%)',
                borderRadius: '6px',
                fontSize: '12px',
              }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, 'Close']}
              labelStyle={{ color: 'hsl(215,20%,55%)' }}
            />
            <Area
              type="monotone"
              dataKey="close"
              stroke={chartColor}
              strokeWidth={1.5}
              fill="url(#priceGrad)"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
      <p className="text-xs text-muted-foreground mt-2">Demo data — illustrative only</p>
    </div>
  )
}
