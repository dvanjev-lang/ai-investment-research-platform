'use client'

import { useState, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'

interface Props { ticker: string }

export function DocumentUpload({ ticker }: Props) {
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const { data: docs, refetch } = useQuery({
    queryKey: ['documents', ticker],
    queryFn: () => api.listDocuments(ticker),
  })

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('ticker', ticker)
      formData.append('document_type', 'annual_report')
      const result = await api.uploadDocument(formData)
      setUploadResult(result)
      refetch()
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-card border border-border rounded-lg p-5">
        <div className="flex items-center gap-2 mb-4">
          <Upload className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold">Document Upload</h3>
        </div>
        <p className="text-sm text-muted-foreground mb-4">
          Upload annual reports, quarterly reports, or investor presentations. The AI Research Assistant will use these documents to answer questions.
        </p>

        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-primary/5 transition-all"
        >
          {uploading ? (
            <Loader2 className="w-8 h-8 text-muted-foreground animate-spin mx-auto" />
          ) : (
            <Upload className="w-8 h-8 text-muted-foreground mx-auto" />
          )}
          <p className="text-sm text-muted-foreground mt-2">
            {uploading ? 'Processing...' : 'Click to upload PDF, TXT, or DOCX'}
          </p>
        </div>
        <input ref={fileRef} type="file" accept=".pdf,.txt,.docx" onChange={handleUpload} className="hidden" />

        {uploadResult && (
          <div className="flex items-center gap-2 mt-3 text-sm text-positive">
            <CheckCircle className="w-4 h-4" />
            Uploaded: {uploadResult.name} ({uploadResult.word_count?.toLocaleString()} words)
          </div>
        )}
      </div>

      {docs && docs.documents.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-5">
          <h4 className="text-sm font-semibold mb-3">Uploaded Documents</h4>
          <div className="space-y-2">
            {docs.documents.map((doc) => (
              <div key={doc.id} className="flex items-center gap-3 text-sm py-2 border-b border-border/50 last:border-0">
                <FileText className="w-4 h-4 text-muted-foreground shrink-0" />
                <span className="font-medium">{doc.name}</span>
                <span className="text-muted-foreground ml-auto">{doc.word_count?.toLocaleString()} words</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
