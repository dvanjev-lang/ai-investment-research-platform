from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.document_service import document_service

router = APIRouter()

_ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
_MAX_FILE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    ticker: str = Form(...),
    document_type: str = Form(default="annual_report"),
    reporting_period: str = Form(default=""),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = ("." + file.filename.rsplit(".", 1)[-1].lower()) if "." in file.filename else ""
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(_ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(content) // 1024} KB). Maximum is {_MAX_FILE_BYTES // 1024 // 1024} MB.",
        )

    result = await document_service.add_document(
        content=content,
        filename=file.filename,
        ticker=ticker,
        doc_type=document_type,
        period=reporting_period,
    )
    return result


@router.get("/{ticker}")
async def list_documents(ticker: str):
    ticker = ticker.upper()
    docs = document_service.get_documents(ticker)
    return {"ticker": ticker, "documents": docs}


@router.get("/document/{doc_id}")
async def get_document(doc_id: str):
    doc = document_service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
