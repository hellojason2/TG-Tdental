import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.api.public_site as public_site_module
import app.main as main_module


@pytest.fixture
def client_with_fallback(monkeypatch, tmp_path):
    fallback_path = tmp_path / "public_consultations.jsonl"

    def _raise_runtime_error():
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(main_module, "init_pool", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "close_pool", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        main_module, "bootstrap_auth_tables", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        main_module, "bootstrap_public_site_tables", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(public_site_module, "get_conn", _raise_runtime_error)
    monkeypatch.setattr(public_site_module, "_fallback_storage_path", lambda: fallback_path)

    with TestClient(main_module.app) as test_client:
        yield test_client, fallback_path


def test_create_consultation_uses_file_fallback_when_db_unavailable(client_with_fallback):
    client, fallback_path = client_with_fallback

    response = client.post(
        "/api/public/consultations",
        json={
            "full_name": "Nguyen Van A",
            "phone": "0909 123 456",
            "email": "a@example.com",
            "service_interest": "Nieng rang",
            "preferred_date": "2026-03-05",
            "message": "Muon tu van nieng rang trong suot",
            "source_page": "contact-page",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["storage"] == "file-fallback"
    assert Path(fallback_path).exists()

    lines = Path(fallback_path).read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    saved = json.loads(lines[0])
    assert saved["full_name"] == "Nguyen Van A"
    assert saved["phone"] == "0909 123 456"
    assert saved["service_interest"] == "Nieng rang"


def test_create_consultation_rejects_invalid_phone(client_with_fallback):
    client, _fallback_path = client_with_fallback

    response = client.post(
        "/api/public/consultations",
        json={
            "full_name": "Nguyen Van B",
            "phone": "invalid-phone",
        },
    )

    assert response.status_code == 422
    assert "So dien thoai" in response.json()["detail"]


def test_create_consultation_rejects_invalid_email(client_with_fallback):
    client, _fallback_path = client_with_fallback

    response = client.post(
        "/api/public/consultations",
        json={
            "full_name": "Nguyen Van C",
            "phone": "0912345678",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422
    assert "Email" in response.json()["detail"]
