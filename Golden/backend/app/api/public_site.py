"""Public marketing-site API routes."""

from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.database import get_conn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/public", tags=["public-site"])

_PHONE_PATTERN = re.compile(r"^[0-9+\-()\s]{7,20}$")
_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS public_consultation_requests (
    id UUID PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(255),
    service_interest VARCHAR(120),
    preferred_date DATE,
    message TEXT,
    source_page VARCHAR(255),
    client_ip VARCHAR(64),
    user_agent TEXT,
    status VARCHAR(32) DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_public_consultation_requests_created_at
ON public_consultation_requests (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_public_consultation_requests_status
ON public_consultation_requests (status);
"""


class ConsultationRequest(BaseModel):
    """Payload for consultation form submissions."""

    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=20)
    email: str | None = Field(default=None, max_length=255)
    service_interest: str | None = Field(default=None, max_length=120)
    preferred_date: date | None = None
    message: str | None = Field(default=None, max_length=2000)
    source_page: str | None = Field(default=None, max_length=255)


def ensure_public_site_tables(conn) -> None:
    """Create public consultation table if it does not exist."""
    with conn.cursor() as cur:
        cur.execute(_TABLES_SQL)


def bootstrap_public_site_tables() -> None:
    """Ensure public-site tables are available during app boot."""
    with get_conn() as conn:
        ensure_public_site_tables(conn)


def _fallback_storage_path() -> Path:
    backend_dir = Path(__file__).resolve().parents[2]
    return backend_dir / "data" / "public_consultations.jsonl"


def _extract_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for", "").strip()
    if forwarded:
        return forwarded.split(",", 1)[0].strip() or None

    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip

    if request.client and request.client.host:
        return request.client.host

    return None


def _validate_input(payload: ConsultationRequest) -> tuple[str, str, str | None]:
    full_name = payload.full_name.strip()
    phone = payload.phone.strip()
    email = payload.email.strip().lower() if payload.email else None

    if not _PHONE_PATTERN.fullmatch(phone):
        raise HTTPException(status_code=422, detail="So dien thoai khong hop le")

    if email and not _EMAIL_PATTERN.fullmatch(email):
        raise HTTPException(status_code=422, detail="Email khong hop le")

    return full_name, phone, email


def _save_fallback(record: dict) -> None:
    """Persist to file if DB is unavailable.

    This keeps the public form operational even during temporary DB outages.
    """
    path = _fallback_storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


@router.post("/consultations")
async def create_consultation(payload: ConsultationRequest, request: Request):
    """Create a consultation request from the static public site."""
    full_name, phone, email = _validate_input(payload)

    submission_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    client_ip = _extract_client_ip(request)
    user_agent = request.headers.get("user-agent")

    service_interest = payload.service_interest.strip() if payload.service_interest else None
    message = payload.message.strip() if payload.message else None
    source_page = payload.source_page.strip() if payload.source_page else None

    fallback_record = {
        "id": submission_id,
        "full_name": full_name,
        "phone": phone,
        "email": email,
        "service_interest": service_interest,
        "preferred_date": payload.preferred_date.isoformat()
        if payload.preferred_date
        else None,
        "message": message,
        "source_page": source_page,
        "client_ip": client_ip,
        "user_agent": user_agent,
        "status": "new",
        "created_at": created_at.isoformat(),
    }

    storage = "database"
    try:
        with get_conn() as conn:
            ensure_public_site_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO public_consultation_requests (
                        id,
                        full_name,
                        phone,
                        email,
                        service_interest,
                        preferred_date,
                        message,
                        source_page,
                        client_ip,
                        user_agent,
                        status,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'new', %s)
                    """,
                    (
                        submission_id,
                        full_name,
                        phone,
                        email,
                        service_interest,
                        payload.preferred_date,
                        message,
                        source_page,
                        client_ip,
                        user_agent,
                        created_at,
                    ),
                )
    except RuntimeError:
        storage = "file-fallback"
        _save_fallback(fallback_record)
    except Exception:
        logger.exception("Failed to persist consultation request to database")
        storage = "file-fallback"
        _save_fallback(fallback_record)

    return {
        "ok": True,
        "id": submission_id,
        "storage": storage,
        "message": "Yeu cau tu van da duoc ghi nhan.",
    }
