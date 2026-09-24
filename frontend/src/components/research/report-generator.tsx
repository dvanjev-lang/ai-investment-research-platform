'use client'

import { useState } from 'react'
import { FileText, Loader2, Download } from 'lucide-react'
import { api, ReportResponse } from '@/lib/api'
import ReactMarkdown from 'react-markdown'

interface Props { ticker: string }

export function ReportGenerator({ ticker }: Props) {
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<ReportResponse | null>(null)

  const generate = async () => {
    setLoading(true)
    try {
      const r = await api.generateReport({ ticker, include_peers: true })
      setReport(r)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-card border border-border rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold">Research Report Generator</h3>
        </div>
        <button
          onClick={generate}
          disabled={loading}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {!report && !loading && (
        <p className="text-sm text-muted-foreground">
          Generate a structured investment research report for {ticker} based on available financial data and documents.
        </p>
      )}

      {report && (
        <div className="space-y-6 mt-4">
          <div className="border-b border-border pb-4">
            <h2 className="text-lg font-semibold">{report.title}</h2>
            <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
              <span>Generated: {new Date(report.generated_at).toLocaleString()}</span>
              <span>Data through: {report.data_through}</span>
            </div>
          </div>

          {report.sections.map((section) => (
            <div key={section.title} className="space-y-2">
              <h3 className="text-sm font-semibold text-foreground">{section.title}</h3>
              <div className="text-sm text-muted-foreground leading-relaxed prose prose-sm prose-invert max-w-none">
                <ReactMarkdown>{section.content}</ReactMarkdown>
              </div>
              {section.citations.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-1">
                  {section.citations.map((c, i) => (
                    <span key={i} className="text-xs bg-muted px-2 py-0.5 rounded text-muted-foreground">
                      {c.source_name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          <div className="pt-4 border-t border-border text-xs text-muted-foreground">
            {report.disclaimer}
          </div>
        </div>
      )}
    </div>
  )
}
