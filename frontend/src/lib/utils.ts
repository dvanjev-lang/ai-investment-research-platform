import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value?: number | null, decimals = 0): string {
  if (value === undefined || value === null) return '—'
  if (Math.abs(value) >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
  if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(1)}B`
  if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(decimals)}M`
  return `$${value.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`
}

export function formatPercent(value?: number | null): string {
  if (value === undefined || value === null) return '—'
  return `${(value * 100).toFixed(1)}%`
}

export function formatMultiple(value?: number | null, decimals = 1): string {
  if (value === undefined || value === null) return '—'
  return `${value.toFixed(decimals)}x`
}

export function formatNumber(value?: number | null, decimals = 0): string {
  if (value === undefined || value === null) return '—'
  return value.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export function changeColor(value?: number | null): string {
  if (value === undefined || value === null) return 'text-muted-foreground'
  if (value > 0) return 'text-positive'
  if (value < 0) return 'text-negative'
  return 'text-muted-foreground'
}
