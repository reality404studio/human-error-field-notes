"""
test_cors.py — Browser CORS is limited to local origins.
"""

from fastapi.testclient import TestClient

from api.main import _LOCAL_ORIGIN_PATTERN, app, is_local_origin


def _cors_kwargs() -> dict:
    middleware = next(
        layer
        for layer in app.user_middleware
        if getattr(layer.cls, "__name__", "") == "CORSMiddleware"
    )
    return middleware.kwargs


def test_only_local_origins_match():
    assert is_local_origin("http://localhost")
    assert is_local_origin("http://localhost:3000")
    assert is_local_origin("http://127.0.0.1:5173")
    assert is_local_origin("https://[::1]:8080")
    assert not is_local_origin("*")
    assert not is_local_origin("https://notes.example.com")
    assert not is_local_origin("http://localhost.evil.com")
    assert not is_local_origin("http://127.0.0.1.evil.com")
    assert not is_local_origin("http://evil.com")


def test_middleware_is_local_only_without_credentials():
    kwargs = _cors_kwargs()
    assert kwargs["allow_origins"] == []
    assert kwargs["allow_origin_regex"] == _LOCAL_ORIGIN_PATTERN
    assert "*" not in kwargs["allow_origin_regex"]
    assert kwargs["allow_credentials"] is False


def test_browser_preflight_allows_local_origins_only():
    client = TestClient(app)

    for origin in (
        "http://localhost:3000",
        "http://127.0.0.1:9999",
        "https://[::1]:4173",
    ):
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

    for origin in ("https://not-allowed.example", "http://localhost.evil.com", "*"):
        blocked = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert blocked.status_code == 400
        assert blocked.headers.get("access-control-allow-origin") != "*"

    direct = client.get("/health", headers={"Origin": "https://not-allowed.example"})
    assert direct.status_code == 200
    assert direct.json()["status"] == "ok"
    assert direct.headers.get("access-control-allow-origin") is None
