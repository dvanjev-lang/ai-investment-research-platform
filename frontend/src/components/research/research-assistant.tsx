'use client'

import { useState } from 'react'
import { Brain, Send, Loader2, ChevronDown, ChevronUp, TrendingUp, AlertTriangle, Database, CheckCircle } from 'lucide-react'
import { api, ResearchQueryResponse, StructuredAnalysis } from '@/lib/api'

interface Props { ticker: string }

const SAMPLE_QUESTIONS = [
  'Summarize the company\'s business model',
  'How has revenue changed over the past 3 years?',
  'What are the main drivers of gross margin?',
  'Describe the key financial risks',
  'How has free cash flow evolved?',
]

const VERDICT_STYLES: Record<string, { bg: string; text: string; dot: string }> = {
  'Positive':           { bg: 'bg-emerald-500/10', text: 'text-emerald-400', dot: 'bg-emerald-400' },
  'Neutral':            { bg: 'bg-blue-500/10',    text: 'text-blue-400',    dot: 'bg-blue-400'    },
  'Cautious':           { bg: 'bg-amber-500/10',   text: 'text-amber-400',   dot: 'bg-amber-400'   },
  'Insufficient Data':  { bg: 'bg-muted',          text: 'text-muted-foreground', dot: 'bg-muted-foreground' },
}

const CONFIDENCE_STYLES: Record<string, string> = {
  'High':   'text-emerald-400',
  'Medium': 'text-amber-400',
  'Low':    'text-muted-foreground',
}

function StructuredResult({ sa, citations }: { sa: StructuredAnalysis; citations: ResearchQueryResponse['citations'] }) {
  const verdict = VERDICT_STYLES[sa.verdict] ?? VERDICT_STYLES['Insufficient Data']
  const confidenceColor = CONFIDENCE_STYLES[sa.confidence] ?? 'text-muted-foreground'

  return (
    <div className="space-y-3">
      {/* Verdict + confidence bar */}
      <div className="flex items-center gap-3">
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold ${verdict.bg} ${verdict.text}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${verdict.dot}`} />
          {sa.verdict}
        </div>
        <span className={`text-xs font-medium ${confidenceColor}`}>
          {sa.confidence} confidence
        </span>
      </div>

      {/* Summary */}
      <div className="text-sm leading-relaxed text-foreground">
        {sa.summary}
      </div>

      {/* Key Findings */}
      {sa.key_findings.length > 0 && (
        <div className="bg-muted/40 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2.5">
            <TrendingUp className="w-3.5 h-3.5 text-primary" />
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Key Findings</span>
          </div>
          <ul className="space-y-1.5">
            {sa.key_findings.map((f, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-primary font-mono mt-0.5 shrink-0">·</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Risks */}
      {sa.risks.length > 0 && (
        <div className="bg-amber-500/5 border border-amber-500/10 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-amber-400/70">Risk Factors</span>
          </div>
          <ul className="space-y-1.5">
            {sa.risks.map((r, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-amber-400 mt-0.5 shrink-0">·</span>
                <span className="text-muted-foreground">{r}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Data Gaps */}
      {sa.data_gaps.length > 0 && (
        <div className="bg-muted/20 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Database className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Data Limitations</span>
          </div>
          <ul className="space-y-1">
            {sa.data_gaps.map((g, i) => (
              <li key={i} className="text-xs text-muted-foreground flex gap-2">
                <span className="shrink-0">·</span>
                <span>{g}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Sources */}
      {citations.length > 0 && (
        <div className="pt-2 border-t border-border">
          <div className="flex items-center gap-2 mb-1.5">
            <CheckCircle className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Sources</span>
          </div>
          <div className="space-y-1">
            {citations.map((c, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                <span className="font-mono text-primary">[{i + 1}]</span>
                <span>{c.source_name}{c.date ? ` — ${c.date}` : ''}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export function ResearchAssistant({ ticker }: Props) {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<ResearchQueryResponse | null>(null)
  const [showTrace, setShowTrace] = useState(false)

  const submit = async (q: string) => {
    if (!q.trim()) return
    setLoading(true)
    setResponse(null)
    try {
      const res = await api.queryResearch({ ticker, question: q, include_financial_data: true, include_documents: true })
      setResponse(res)
    } catch {
      setResponse({
        question: q,
        answer: 'Error communicating with the research service. Make sure the backend is running.',
        citations: [],
        agent_trace: [],
        disclaimer: '',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Input */}
      <div className="bg-card border border-border rounded-lg p-5">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold">AI Research Assistant</h3>
          <span className="text-xs bg-muted px-2 py-0.5 rounded text-muted-foreground ml-auto">
            Not investment advice
          </span>
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && submit(question)}
            placeholder={`Ask about ${ticker}...`}
            className="flex-1 bg-muted border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-primary transition-colors"
          />
          <button
            onClick={() => submit(question)}
            disabled={loading || !question.trim()}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mt-3">
          {SAMPLE_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => { setQuestion(q); submit(q) }}
              className="text-xs px-2.5 py-1 bg-muted rounded-full text-muted-foreground hover:text-foreground hover:bg-muted/70 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Response */}
      {response && (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="px-5 py-3 border-b border-border bg-muted/30">
            <p className="text-xs text-muted-foreground font-medium">Q: {response.question}</p>
          </div>
          <div className="p-5">
            {response.structured_analysis ? (
              <StructuredResult sa={response.structured_analysis} citations={response.citations} />
            ) : (
              <>
                <p className="text-sm leading-relaxed">{response.answer}</p>
                {response.citations.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-border space-y-1">
                    {response.citations.map((c, i) => (
                      <div key={i} className="flex gap-2 text-xs text-muted-foreground">
                        <span className="font-mono text-primary">[{i + 1}]</span>
                        <span>{c.source_name}</span>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}

            {/* Agent trace */}
            {response.agent_trace.length > 0 && (
              <div className="mt-4">
                <button
                  onClick={() => setShowTrace(!showTrace)}
                  className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showTrace ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  Agent trace ({response.agent_trace.length} steps)
                </button>
                {showTrace && (
                  <div className="mt-2 space-y-2">
                    {response.agent_trace.map((step, i) => (
                      <div key={i} className="flex gap-2 text-xs bg-muted/50 rounded px-3 py-2">
                        <span className="font-mono text-primary font-medium w-36 shrink-0">{step.agent}</span>
                        <span className="text-muted-foreground">{step.result_summary}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {response.disclaimer && (
              <p className="text-xs text-muted-foreground mt-4 pt-4 border-t border-border">
                {response.disclaimer}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
