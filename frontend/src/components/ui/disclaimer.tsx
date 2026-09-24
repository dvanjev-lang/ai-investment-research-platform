import { AlertCircle } from 'lucide-react'

export function Disclaimer() {
  return (
    <div className="flex gap-3 p-4 bg-muted/50 border border-border rounded-lg text-xs text-muted-foreground">
      <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
      <p>
        <strong>Disclaimer:</strong> This platform provides informational and analytical content for educational
        and research purposes only. It does not constitute investment advice, a recommendation to buy or sell
        any security, or a guarantee of future performance. All financial data shown is{' '}
        <strong>demo/illustrative data</strong>. Always verify financial information independently.
      </p>
    </div>
  )
}
