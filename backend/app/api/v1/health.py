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


def _chat_completions_check(api_key: str, model: str, timeout: float = 30.0) -> str:
    """Minimal chat completions call to verify the endpoint works end-to-end."""
    if not api_key:
        return "no_key"
    import json as _json
    try:
        ctx = ssl.create_default_context()
        payload = _json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
            "max_tokens": 5,
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            data = _json.loads(resp.read())
            reply = data["choices"][0]["message"]["content"].strip()
            return f"ok — model replied: {reply!r}"
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        retry_after = e.headers.get("Retry-After", "n/a")
        return f"http_error: {e.code} retry-after={retry_after} body={body}"
    except Exception as e:
        return f"fail: {type(e).__name__}: {e}"


@router.get("/health")
async def health(chat_test: bool = False):
    result = {
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
    # Only run the expensive chat completions test when explicitly requested
    if chat_test:
        result["openai_chat_test"] = _chat_completions_check(
            settings.OPENAI_API_KEY, settings.OPENAI_CHAT_MODEL
        )
    return result
