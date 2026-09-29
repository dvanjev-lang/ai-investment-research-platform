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


def _anthropic_check(api_key: str, model: str) -> str:
    """Minimal Anthropic messages call to verify the endpoint works end-to-end."""
    if not api_key:
        return "no_key"
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Reply with the single word: ok"}],
        )
        reply = msg.content[0].text.strip()
        return f"ok — model replied: {reply!r}"
    except Exception as e:
        return f"fail: {type(e).__name__}: {e}"


@router.get("/health")
async def health(chat_test: bool = False):
    result = {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "data_provider": settings.DATA_PROVIDER,
        "ai_enabled": bool(settings.ANTHROPIC_API_KEY),
        "ai_provider": "anthropic" if settings.ANTHROPIC_API_KEY else "none",
    }
    # Only run the expensive LLM test when explicitly requested
    if chat_test:
        result["anthropic_chat_test"] = _anthropic_check(
            settings.ANTHROPIC_API_KEY, settings.ANTHROPIC_MODEL
        )
    return result
