'use client'

import { useState } from 'react'
import { Brain, Send, Loader2, ChevronDown, ChevronUp } from 'lucide-react'
import { api, ResearchQueryResponse } from '@/lib/api'
import ReactMarkdown from 'react-markdown'

interface Props { ticker: string }

const SAMPLE_QUESTIONS = [
  'Summarize the company\'s business model',
  'How has revenue changed over the past 3 years?',
  'What are the main drivers of gross margin?',
  'Describe the key financial risks',
  'How has free cash flow evolved?',
]

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
    } catch (e) {
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

        {/* Sample questions */}
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
          <div className="px-5 py-4 border-b border-border bg-muted/30">
            <p className="text-xs text-muted-foreground font-medium">Q: {response.question}</p>
          </div>
          <div className="p-5">
            <div className="prose prose-sm prose-invert max-w-none text-sm leading-relaxed text-foreground">
              <ReactMarkdown>{response.answer}</ReactMarkdown>
            </div>

            {/* Citations */}
            {response.citations.length > 0 && (
              <div className="mt-4 pt-4 border-t border-border">
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Sources</div>
                <div className="space-y-1.5">
                  {response.citations.map((c, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                      <span className="font-mono text-primary">[{i + 1}]</span>
                      <span>{c.source_name}{c.date ? ` — ${c.date}` : ''}</span>
                    </div>
                  ))}
                </div>
              </div>
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
