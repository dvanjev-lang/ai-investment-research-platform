"""
AI Investment Research Platform — FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import companies, documents, research, valuation, health
from app.core.config import settings

app = FastAPI(
    title="AI Investment Research Platform",
    description=(
        "A financial research platform for analyzing public companies. "
        "Provides factual financial data, document analysis, and AI-assisted research. "
        "NOT investment advice."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Allow all origins in demo/mock mode; restrict in production with real auth
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def root():
    return {"status": "ok", "version": "1.0.0"}


app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(valuation.router, prefix="/api/v1/valuation", tags=["Valuation"])
