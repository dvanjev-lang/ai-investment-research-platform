from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "data_provider": settings.DATA_PROVIDER,
        "ai_enabled": bool(settings.OPENAI_API_KEY),
    }
