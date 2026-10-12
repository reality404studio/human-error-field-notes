"""
test_cors.py — CORS allowlist for the API
"""

from fastapi.testclient import TestClient

from api.main import (
    _DEFAULT_ALLOWED_ORIGINS,
    app,
    parse_allowed_origins,
)


def _cors_kwargs() -> dict:
    middleware = next(
        layer
        for layer in app.user_middleware
        if getattr(layer.cls, "__name__", "") == "CORSMiddleware"
    )
    return middleware.kwargs


def test_blank_origins_use_local_defaults():
    assert parse_allowed_origins(None) == _DEFAULT_ALLOWED_ORIGINS
    assert parse_allowed_origins("  ") == _DEFAULT_ALLOWED_ORIGINS
    assert parse_allowed_origins("*, *") == _DEFAULT_ALLOWED_ORIGINS
    assert "*" not in parse_allowed_origins("*")


def test_explicit_origins_are_trimmed_and_deduped():
    parsed = parse_allowed_origins(
        " https://notes.example.com/ , http://localhost:5173/ , *, https://notes.example.com "
    )
    assert parsed == ["https://notes.example.com", "http://localhost:5173"]
    assert "*" not in parsed


def test_middleware_never_uses_wildcard_or_credentials():
    kwargs = _cors_kwargs()
    assert kwargs["allow_origins"]
    assert "*" not in kwargs["allow_origins"]
    assert kwargs["allow_credentials"] is False


def test_browser_preflight_echoes_allowlisted_origin_only():
    client = TestClient(app)
    origin = _cors_kwargs()["allow_origins"][0]

    allowed = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == origin
    assert "access-control-allow-credentials" not in allowed.headers

    blocked = client.options(
        "/health",
        headers={
            "Origin": "https://not-allowed.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert blocked.status_code == 400
    assert blocked.headers.get("access-control-allow-origin") != "*"

    # Non-browser clients still receive the response. The browser, not the
    # server, hides it when the origin is outside the allowlist.
    direct = client.get("/health", headers={"Origin": "https://not-allowed.example"})
    assert direct.status_code == 200
    assert direct.json()["status"] == "ok"
    assert direct.headers.get("access-control-allow-origin") is None
