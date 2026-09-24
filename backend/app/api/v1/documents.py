from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import uuid
import io

router = APIRouter()

# In-memory store for demo (replace with DB + S3 in production)
_document_store: dict = {}
_chunk_store: dict = {}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    ticker: str = Form(...),
    document_type: str = Form(default="annual_report"),
    reporting_period: str = Form(default=""),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed = {".pdf", ".txt", ".docx"}
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    doc_id = str(uuid.uuid4())

    # Extract text (basic demo — full pipeline: PyPDF2, chunking, embeddings)
    text = ""
    if ext == ".txt":
        text = content.decode("utf-8", errors="ignore")
    elif ext == ".pdf":
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            text = f"PDF extraction partial: {str(e)}"

    _document_store[doc_id] = {
        "id": doc_id,
        "ticker": ticker.upper(),
        "name": file.filename,
        "document_type": document_type,
        "reporting_period": reporting_period,
        "text": text[:50000],  # cap for demo
        "word_count": len(text.split()),
        "is_processed": True,
    }

    return {
        "document_id": doc_id,
        "ticker": ticker.upper(),
        "name": file.filename,
        "word_count": len(text.split()),
        "status": "processed",
        "note": "Demo mode: document stored in memory. Use persistent storage in production.",
    }


@router.get("/{ticker}")
async def list_documents(ticker: str):
    ticker = ticker.upper()
    docs = [v for v in _document_store.values() if v["ticker"] == ticker]
    return {"ticker": ticker, "documents": docs}


@router.get("/document/{doc_id}")
async def get_document(doc_id: str):
    doc = _document_store.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
