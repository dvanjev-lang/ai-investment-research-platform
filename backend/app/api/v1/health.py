import os
import socket
import ssl
import urllib.request
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


def _urllib_check(api_key: str, timeout: float = 8.0) -> str:
    if not api_key:
        return "no_key"
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            return f"ok (HTTP {resp.status})"
    except urllib.error.HTTPError as e:
        return f"http_error: {e.code}"
    except Exception as e:
        return f"fail: {type(e).__name__}: {e}"


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "data_provider": settings.DATA_PROVIDER,
        "ai_enabled": bool(settings.OPENAI_API_KEY),
        "openai_tcp_tls": _tcp_tls_check("api.openai.com", 443),
        "openai_http_urllib": _urllib_check(settings.OPENAI_API_KEY),
        "proxy_env": {
            "HTTPS_PROXY": os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "not set",
            "HTTP_PROXY": os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or "not set",
        },
    }
