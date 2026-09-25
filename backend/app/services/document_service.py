"""
Document Service — chunking, embedding, and semantic retrieval.

Retrieval modes:
  • semantic  — OpenAI text-embedding-3-small + cosine similarity (when API key present)
  • tfidf     — pure-Python TF-IDF fallback (no external deps, no API key needed)

Pipeline:
  upload → extract text → chunk (512 tok, 64-tok overlap) → embed → store
  query  → embed query → cosine similarity → top-k chunks → cited context
"""

import io
import math
import re
import uuid
from collections import defaultdict
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Prompt-injection sanitizer
# ---------------------------------------------------------------------------

# Patterns that could attempt to override LLM instructions
_INJECTION_PATTERNS: list[re.Pattern] = [
    # Classic direct instruction override
    re.compile(r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions?', re.IGNORECASE),
    re.compile(r'disregard\s+(all\s+)?(previous|prior|above)\s+instructions?', re.IGNORECASE),
    re.compile(r'forget\s+(all\s+)?(previous|prior|above)\s+instructions?', re.IGNORECASE),
    # Role-switch attempts
    re.compile(r'\n\s*(system|assistant|user)\s*:\s*', re.IGNORECASE),
    re.compile(r'<\s*(system|assistant|user)\s*>', re.IGNORECASE),
    # OpenAI special tokens
    re.compile(r'<\|im_start\|>', re.IGNORECASE),
    re.compile(r'<\|im_end\|>', re.IGNORECASE),
    re.compile(r'<\|endoftext\|>', re.IGNORECASE),
    # Prompt-boundary tricks
    re.compile(r'={3,}.*?new\s+(prompt|instructions?|task)', re.IGNORECASE),
    re.compile(r'-{3,}.*?new\s+(prompt|instructions?|task)', re.IGNORECASE),
    # "Act as" / DAN-style
    re.compile(r'\b(act\s+as|pretend\s+(to\s+be|you\s+are)|you\s+are\s+now)\b.*?(AI|assistant|GPT|LLM)', re.IGNORECASE),
    # Direct instruction injection via triple-tick code block heading
    re.compile(r'```\s*system', re.IGNORECASE),
]


def sanitize_for_llm(text: str) -> str:
    """
    Strip or neutralise prompt-injection patterns from untrusted document text.

    Strategy: replace matched injection phrases with [REDACTED] rather than
    silently deleting them, so analysts can see that sanitisation occurred.
    This is defence-in-depth — the system prompt also labels document content
    as untrusted external data.
    """
    for pattern in _INJECTION_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text

# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def _extract_pdf(content: bytes) -> str:
    import PyPDF2
    reader = PyPDF2.PdfReader(io.BytesIO(content))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def _extract_docx(content: bytes) -> str:
    try:
        import docx  # python-docx
        doc = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        return "[python-docx not installed — .docx extraction unavailable]"


def extract_text(content: bytes, ext: str) -> str:
    """Extract plain text from uploaded file bytes."""
    try:
        if ext == ".txt":
            return content.decode("utf-8", errors="ignore")
        elif ext == ".pdf":
            return _extract_pdf(content)
        elif ext == ".docx":
            return _extract_docx(content)
    except Exception as exc:
        return f"[Extraction error: {exc}]"
    return ""


# ---------------------------------------------------------------------------
# Chunker — tiktoken-based, 512 tokens with 64-token overlap
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_tokens: int = 512, overlap_tokens: int = 64) -> list[str]:
    """
    Split text into overlapping chunks by token count.
    Uses cl100k_base (GPT-4 tokenizer) via tiktoken.
    Falls back to word-based splitting if tiktoken unavailable.
    """
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + chunk_tokens, len(tokens))
            chunk = enc.decode(tokens[start:end])
            chunks.append(chunk)
            if end >= len(tokens):
                break
            start += chunk_tokens - overlap_tokens
        return [c for c in chunks if c.strip()]
    except Exception:
        # Word-based fallback (~1.3 words per token on average)
        words = text.split()
        word_chunk = max(1, chunk_tokens // 1)
        word_overlap = max(0, overlap_tokens // 1)
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + word_chunk, len(words))
            chunks.append(" ".join(words[start:end]))
            if end >= len(words):
                break
            start += word_chunk - word_overlap
        return [c for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# TF-IDF fallback search
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return re.findall(r'\b[a-z]+\b', text.lower())


def tfidf_search(query: str, candidates: list[dict], top_k: int) -> list[dict]:
    """
    Pure-Python BM25-style TF-IDF ranking. No external dependencies.
    Returns up to top_k candidates sorted by relevance score, score > 0 only.
    """
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    # Document frequency
    df: dict[str, int] = defaultdict(int)
    for chunk in candidates:
        for term in set(_tokenize(chunk["text"])):
            df[term] += 1
    N = len(candidates)
    idf = {t: math.log((N + 1) / (n + 1)) + 1.0 for t, n in df.items()}

    scored = []
    for chunk in candidates:
        chunk_terms = _tokenize(chunk["text"])
        total = len(chunk_terms) or 1
        tf: dict[str, float] = defaultdict(float)
        for t in chunk_terms:
            tf[t] += 1

        score = sum(
            (tf[t] / total) * idf.get(t, 0.0)
            for t in query_terms
        )
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, chunk in scored[:top_k]:
        results.append({**chunk, "score": round(score, 6), "retrieval_mode": "tfidf"})
    return results


# ---------------------------------------------------------------------------
# DocumentService
# ---------------------------------------------------------------------------

class DocumentService:
    """
    In-memory document store with real embedding support.

    Documents:  doc_id → metadata dict
    Chunks:     doc_id → list of chunk dicts
    _all_chunks flat list for cross-document search
    """

    def __init__(self) -> None:
        self._documents: dict[str, dict] = {}
        self._chunks: dict[str, list[dict]] = {}
        self._all_chunks: list[dict] = []

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------

    async def add_document(
        self,
        content: bytes,
        filename: str,
        ticker: str,
        doc_type: str = "annual_report",
        period: str = "",
    ) -> dict:
        """
        Extract text, chunk, embed, store.
        Returns metadata dict including retrieval_mode.
        """
        ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
        text = extract_text(content, ext)

        if not text.strip():
            text = "[No extractable text found in this document.]"

        # Cap before chunking to avoid very long embedding batches
        truncated = text[:120_000]
        raw_chunks = chunk_text(truncated)

        doc_id = str(uuid.uuid4())
        embeddings = await self._embed_texts(raw_chunks)
        has_embeddings = any(e is not None for e in embeddings)

        chunks: list[dict] = []
        for idx, (chunk_text_str, emb) in enumerate(zip(raw_chunks, embeddings)):
            safe_text = sanitize_for_llm(chunk_text_str)
            chunks.append({
                "chunk_id": f"{doc_id}_{idx}",
                "doc_id": doc_id,
                "ticker": ticker.upper(),
                "doc_name": filename,
                "doc_type": doc_type,
                "chunk_index": idx,
                "text": safe_text,
                "embedding": emb,  # np.ndarray | None
            })

        meta = {
            "id": doc_id,
            "ticker": ticker.upper(),
            "name": filename,
            "document_type": doc_type,
            "reporting_period": period,
            "word_count": len(text.split()),
            "chunk_count": len(chunks),
            "has_embeddings": has_embeddings,
            "retrieval_mode": "semantic" if has_embeddings else "tfidf",
            "is_processed": True,
        }

        self._documents[doc_id] = meta
        self._chunks[doc_id] = chunks
        self._all_chunks.extend(chunks)

        return {
            "document_id": doc_id,
            "ticker": ticker.upper(),
            "name": filename,
            "word_count": meta["word_count"],
            "chunk_count": len(chunks),
            "retrieval_mode": meta["retrieval_mode"],
            "status": "processed",
        }

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    async def search(
        self,
        ticker: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search documents for a given ticker.

        Returns a list of chunk dicts with added keys:
            score         float  — relevance score (0–1 for cosine, unnormalised for TF-IDF)
            retrieval_mode str   — "semantic" or "tfidf"
        """
        ticker = ticker.upper()
        candidates = [c for c in self._all_chunks if c["ticker"] == ticker]
        if not candidates:
            return []

        from app.core.config import settings
        use_embeddings = (
            bool(settings.OPENAI_API_KEY)
            and all(c["embedding"] is not None for c in candidates)
        )

        if use_embeddings:
            results = await self._embedding_search(query, candidates, top_k)
            if results:
                return results
            # Fall through to TF-IDF if embedding query fails

        return tfidf_search(query, candidates, top_k)

    # ------------------------------------------------------------------
    # Document metadata access
    # ------------------------------------------------------------------

    def get_documents(self, ticker: str) -> list[dict]:
        return [v for v in self._documents.values() if v["ticker"] == ticker.upper()]

    def get_document(self, doc_id: str) -> Optional[dict]:
        return self._documents.get(doc_id)

    # ------------------------------------------------------------------
    # Internal embedding helpers
    # ------------------------------------------------------------------

    async def _embed_texts(self, texts: list[str]) -> list[Optional[np.ndarray]]:
        """
        Embed a list of texts using OpenAI text-embedding-3-small.
        Returns list of np.ndarray (float32) or None entries when unavailable.
        """
        from app.core.config import settings
        if not settings.OPENAI_API_KEY:
            return [None] * len(texts)

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            embeddings: list[Optional[np.ndarray]] = []
            batch_size = 100  # API limit: 2048, but keep batches manageable
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                response = await client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    input=batch,
                )
                for item in response.data:
                    embeddings.append(np.array(item.embedding, dtype=np.float32))
            return embeddings
        except Exception:
            return [None] * len(texts)

    async def _embedding_search(
        self,
        query: str,
        candidates: list[dict],
        top_k: int,
    ) -> list[dict]:
        """Cosine similarity search using OpenAI embeddings."""
        try:
            from openai import AsyncOpenAI
            from app.core.config import settings
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            resp = await client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=[query],
            )
            q_emb = np.array(resp.data[0].embedding, dtype=np.float32)
            q_norm = np.linalg.norm(q_emb)

            scored = []
            for chunk in candidates:
                if chunk["embedding"] is not None:
                    c_emb: np.ndarray = chunk["embedding"]
                    cosine = float(
                        np.dot(q_emb, c_emb) / (q_norm * np.linalg.norm(c_emb) + 1e-9)
                    )
                    scored.append((cosine, chunk))

            scored.sort(key=lambda x: x[0], reverse=True)
            results = []
            for score, chunk in scored[:top_k]:
                results.append({**chunk, "score": round(score, 6), "retrieval_mode": "semantic"})
            return results
        except Exception:
            return []


# Module-level singleton — imported by documents.py and research.py
document_service = DocumentService()
