from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import app.api.auth as auth_module
import app.core.middleware as middleware_module
import app.main as main_module
from app.core.security import hash_password


class FakeAuthDB:
    def __init__(self) -> None:
        admin_id = str(uuid4())
        admin = {
            "id": admin_id,
            "name": "Admin",
            "email": "admin@tdental.vn",
            "password": hash_password("admin123"),
            "role": "admin",
            "active": True,
        }
        self.users_by_email = {admin["email"]: admin}
        self.users_by_id = {admin["id"]: admin}
        self.sessions: dict[str, dict] = {}

    @contextmanager
    def get_conn(self):
        yield FakeConn(self)


class FakeConn:
    def __init__(self, db: FakeAuthDB) -> None:
        self.db = db

    def cursor(self, *args, **kwargs):
        return FakeCursor(self.db)


class FakeCursor:
    def __init__(self, db: FakeAuthDB) -> None:
        self.db = db
        self._one = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql: str, params=None):
        normalized = " ".join(sql.split()).lower()
        params = params or ()

        if normalized.startswith(
            "select id, name, email, password, role, active from app_users"
        ):
            email = str(params[0]).strip().lower()
            user = self.db.users_by_email.get(email)
            if not user or not user["active"]:
                self._one = None
                return
            self._one = (
                user["id"],
                user["name"],
                user["email"],
                user["password"],
                user["role"],
                user["active"],
            )
            return

        if normalized.startswith("insert into app_sessions"):
            _session_id, user_id, token, expires_at = params
            self.db.sessions[str(token)] = {
                "user_id": str(user_id),
                "expires_at": expires_at,
            }
            self._one = None
            return

        if "from app_sessions s join app_users u on u.id = s.user_id" in normalized:
            token = str(params[0])
            session = self.db.sessions.get(token)
            if session is None:
                self._one = None
                return

            expires_at = session["expires_at"]
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at <= datetime.now(timezone.utc):
                self._one = None
                return

            user = self.db.users_by_id.get(session["user_id"])
            if not user or not user["active"]:
                self._one = None
                return
            self._one = (user["id"], user["name"], user["email"], user["role"])
            return

        if normalized.startswith("delete from app_sessions where token = %s"):
            token = str(params[0])
            self.db.sessions.pop(token, None)
            self._one = None
            return

        if normalized.startswith("update app_users set password = %s, updated_at = now() where id = %s"):
            new_password, user_id = params
            user = self.db.users_by_id.get(str(user_id))
            if user:
                user["password"] = str(new_password)
                self.db.users_by_email[user["email"].lower()] = user
            self._one = None
            return

        raise AssertionError(f"Unhandled SQL in test double: {sql}")

    def fetchone(self):
        return self._one


@pytest.fixture
def fake_db():
    return FakeAuthDB()


@pytest.fixture
def client(monkeypatch, fake_db):
    monkeypatch.setattr(main_module, "init_pool", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "close_pool", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        main_module, "bootstrap_auth_tables", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(auth_module, "get_conn", fake_db.get_conn)
    monkeypatch.setattr(middleware_module, "get_conn", fake_db.get_conn)
    middleware_module.reset_login_rate_limit_state()

    with TestClient(main_module.app) as test_client:
        yield test_client

    middleware_module.reset_login_rate_limit_state()


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_session_logout_and_protected_behavior(client, fake_db):
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@tdental.vn", "password": "admin123"},
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert "token" in payload
    assert payload["user"]["role"] == "admin"

    token = payload["token"]
    assert token in fake_db.sessions
    assert login_response.cookies.get("tdental_session") == token

    by_header = client.get(
        "/api/auth/session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert by_header.status_code == 200
    assert by_header.json()["user"]["id"] == payload["user"]["id"]

    by_cookie = client.get("/api/auth/session")
    assert by_cookie.status_code == 200
    assert by_cookie.json()["user"]["email"] == "admin@tdental.vn"

    root_ok = client.get("/")
    assert root_ok.status_code == 200
    assert '<div id="app">' in root_ok.text

    login_redirect = client.get("/login", follow_redirects=False)
    assert login_redirect.status_code in (302, 307)
    assert login_redirect.headers["location"] == "/"

    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_response.status_code == 200
    assert token not in fake_db.sessions

    after_logout = client.get(
        "/api/auth/session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert after_logout.status_code == 401

    protected_redirect = client.get("/app", follow_redirects=False)
    assert protected_redirect.status_code in (302, 307)
    assert protected_redirect.headers["location"] == "/login"


def test_protected_route_requires_auth(client):
    response = client.get("/api/auth/session")
    assert response.status_code == 401

    bad = client.get(
        "/api/auth/session",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert bad.status_code == 401


def test_root_redirects_to_login_without_session(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/login"


def test_password_hash_uses_bcrypt_format():
    hashed = hash_password("temporary-secret")
    assert hashed.startswith("$2")


def test_login_rate_limit_blocks_sixth_failed_attempt(client):
    for _ in range(5):
        failed = client.post(
            "/api/auth/login",
            json={"email": "admin@tdental.vn", "password": "wrong-password"},
        )
        assert failed.status_code == 401

    blocked = client.post(
        "/api/auth/login",
        json={"email": "admin@tdental.vn", "password": "wrong-password"},
    )
    assert blocked.status_code == 429


def test_login_cookie_flags_can_be_hardened_for_production(client):
    original_secure = auth_module.settings.COOKIE_SECURE
    original_samesite = auth_module.settings.COOKIE_SAMESITE
    auth_module.settings.COOKIE_SECURE = True
    auth_module.settings.COOKIE_SAMESITE = "strict"
    try:
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin@tdental.vn", "password": "admin123"},
        )
    finally:
        auth_module.settings.COOKIE_SECURE = original_secure
        auth_module.settings.COOKIE_SAMESITE = original_samesite

    assert login_response.status_code == 200
    set_cookie_header = login_response.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie_header
    assert "Secure" in set_cookie_header
    assert "SameSite=strict" in set_cookie_header


def test_security_headers_and_cors_rejection(client):
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["x-frame-options"] == "DENY"

    preflight = client.options(
        "/api/auth/login",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert preflight.status_code == 400
    assert "access-control-allow-origin" not in preflight.headers
