import socket
import ssl
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


def _tcp_tls_check(host: str, port: int, timeout: float = 5.0) -> str:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                return f"ok (TLS {ssock.version()})"
    except ssl.SSLError as e:
        return f"tls_fail: {e}"
    except OSError as e:
        return f"tcp_fail: {e}"
    except Exception as e:
        return f"error: {e}"


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "data_provider": settings.DATA_PROVIDER,
        "ai_enabled": bool(settings.OPENAI_API_KEY),
        "openai_connectivity": _tcp_tls_check("api.openai.com", 443),
    }
