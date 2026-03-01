"""Appointments, calendar, and reception APIs."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, time
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field, model_validator

from app.core.database import get_conn
from app.core.lookup_sql import (
    TableRef,
    empty_page,
    page_window,
    pick_column,
    quote_ident,
    resolve_table,
    table_columns,
)
from app.core.middleware import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/appointments",
    tags=["appointments"],
    dependencies=[Depends(require_auth)],
)

APPOINTMENT_STATES = (
    "waiting",
    "confirmed",
    "arrived",
    "in_progress",
    "done",
    "cancel",
)

STATE_TRANSITIONS: dict[str, set[str]] = {
    "waiting": {"waiting", "confirmed", "arrived", "cancel"},
    "confirmed": {"confirmed", "waiting", "arrived", "cancel"},
    "arrived": {"arrived", "in_progress", "cancel", "waiting"},
    "in_progress": {"in_progress", "done", "cancel"},
    "done": {"done"},
    "cancel": {"cancel", "waiting", "confirmed"},
}

CALENDAR_START_HOUR = 6
CALENDAR_END_HOUR = 23
CALENDAR_SLOT_MINUTES = 30

APPOINTMENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS app_appointments (
    id UUID PRIMARY KEY,
    company_id TEXT,
    partner_id TEXT,
    patient_name TEXT NOT NULL,
    patient_phone TEXT,
    doctor_id TEXT,
    doctor_name TEXT,
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    state TEXT NOT NULL DEFAULT 'waiting',
    services JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT app_appointments_state_check
        CHECK (state IN ('waiting', 'confirmed', 'arrived', 'in_progress', 'done', 'cancel'))
);

CREATE INDEX IF NOT EXISTS idx_app_appointments_day ON app_appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_app_appointments_state ON app_appointments(state);
CREATE INDEX IF NOT EXISTS idx_app_appointments_company_id ON app_appointments(company_id);
CREATE INDEX IF NOT EXISTS idx_app_appointments_doctor_id ON app_appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_app_appointments_active ON app_appointments(active);
"""


class AppointmentCreate(BaseModel):
    companyId: str | None = None
    partnerId: str | None = None
    patientName: str = Field(min_length=1)
    patientPhone: str | None = None
    doctorId: str | None = None
    doctorName: str | None = None
    appointmentDate: date
    startTime: time
    endTime: time | None = None
    state: str = "waiting"
    services: list[str] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.endTime and self.endTime <= self.startTime:
            raise ValueError("endTime must be later than startTime")
        self.state = _normalize_state_value(self.state)
        return self


class AppointmentUpdate(BaseModel):
    companyId: str | None = None
    partnerId: str | None = None
    patientName: str | None = None
    patientPhone: str | None = None
    doctorId: str | None = None
    doctorName: str | None = None
    appointmentDate: date | None = None
    startTime: time | None = None
    endTime: time | None = None
    state: str | None = None
    services: list[str] | None = None
    notes: str | None = None


class AppointmentStatePatch(BaseModel):
    state: str

    @model_validator(mode="after")
    def normalize_state(self):
        self.state = _normalize_state_value(self.state)
        return self


@dataclass(frozen=True)
class AppointmentColumnMap:
    id: str
    company_id: str | None
    partner_id: str | None
    patient_name: str | None
    patient_phone: str | None
    doctor_id: str | None
    doctor_name: str | None
    appointment_date: str | None
    start_time: str | None
    end_time: str | None
    state: str | None
    services: str | None
    notes: str | None
    active: str | None
    deleted_at: str | None
    created_at: str | None
    updated_at: str | None


@dataclass(frozen=True)
class AppointmentContext:
    ref: TableRef
    columns: tuple[str, ...]
    mapping: AppointmentColumnMap
    is_bootstrap: bool


def _normalize_state_value(raw: str | None) -> str:
    if raw is None:
        raise ValueError("state is required")

    normalized = raw.strip().lower().replace(" ", "_")
    aliases = {
        "inprogress": "in_progress",
        "in-progress": "in_progress",
        "completed": "done",
        "complete": "done",
        "canceled": "cancel",
        "cancelled": "cancel",
        "confirm": "confirmed",
    }
    normalized = aliases.get(normalized, normalized)

    if normalized not in APPOINTMENT_STATES:
        raise ValueError(f"Unsupported appointment state: {raw}")
    return normalized


def _normalize_services(raw_value) -> list[str]:
    if raw_value is None:
        return []

    if isinstance(raw_value, list):
        values: list[str] = []
        for item in raw_value:
            if isinstance(item, dict):
                label = item.get("name") or item.get("label") or item.get("service")
                if label:
                    values.append(str(label).strip())
                continue
            if item is not None:
                values.append(str(item).strip())
        return [item for item in values if item]

    if isinstance(raw_value, dict):
        return _normalize_services([raw_value])

    text = str(raw_value).strip()
    if not text:
        return []

    if text[0] in "[{":
        try:
            parsed = json.loads(text)
            return _normalize_services(parsed)
        except json.JSONDecodeError:
            pass

    if ";" in text:
        parts = [chunk.strip() for chunk in text.split(";")]
    elif "," in text:
        parts = [chunk.strip() for chunk in text.split(",")]
    else:
        parts = [text]

    return [item for item in parts if item]


def _format_time(value: time | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%H:%M")


def _parse_time(value: str | time | None) -> time | None:
    if value is None or isinstance(value, time):
        return value

    raw = str(value).strip()
    if not raw:
        return None

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(raw, fmt).time()
        except ValueError:
            continue

    return None


def _parse_date(value: str | date | None) -> date | None:
    if value is None or isinstance(value, date):
        return value

    raw = str(value).strip()
    if not raw:
        return None

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(raw).date()
    except ValueError:
        return None


def _parse_iso_datetime(value: str | None) -> str | None:
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(raw, fmt).isoformat()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(raw).isoformat()
    except ValueError:
        return raw


def _ensure_bootstrap_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(APPOINTMENTS_TABLE_SQL)


def _build_context(conn, ref: TableRef, *, is_bootstrap: bool) -> AppointmentContext | None:
    columns = table_columns(conn, ref)
    mapped = AppointmentColumnMap(
        id=pick_column(columns, "id", "appointment_id", "appointmentid") or "",
        company_id=pick_column(columns, "company_id", "companyid", "branch_id", "branchid"),
        partner_id=pick_column(
            columns,
            "partner_id",
            "partnerid",
            "customer_id",
            "customerid",
            "patient_id",
            "patientid",
        ),
        patient_name=pick_column(
            columns,
            "patient_name",
            "patientname",
            "partner_name",
            "partnername",
            "customer_name",
            "customername",
            "name",
            "fullname",
        ),
        patient_phone=pick_column(
            columns,
            "patient_phone",
            "patientphone",
            "partner_phone",
            "partnerphone",
            "phone",
            "mobile",
        ),
        doctor_id=pick_column(
            columns,
            "doctor_id",
            "doctorid",
            "employee_id",
            "employeeid",
            "dentist_id",
            "dentistid",
            "user_id",
            "userid",
        ),
        doctor_name=pick_column(
            columns,
            "doctor_name",
            "doctorname",
            "employee_name",
            "employeename",
            "dentist_name",
            "dentistname",
            "doctor",
        ),
        appointment_date=pick_column(
            columns,
            "appointment_date",
            "appointmentdate",
            "date",
            "date_exam",
            "dateexam",
            "date_order",
            "dateorder",
            "exam_date",
            "examdate",
        ),
        start_time=pick_column(
            columns,
            "start_time",
            "starttime",
            "time_start",
            "timestart",
            "from_time",
            "fromtime",
            "hour",
        ),
        end_time=pick_column(
            columns,
            "end_time",
            "endtime",
            "time_end",
            "timeend",
            "to_time",
            "totime",
        ),
        state=pick_column(columns, "state", "status", "appointment_state", "appointmentstate"),
        services=pick_column(
            columns,
            "services",
            "service_names",
            "service_name",
            "service",
            "service_list",
            "servicelist",
        ),
        notes=pick_column(columns, "notes", "note", "description", "reason", "content"),
        active=pick_column(columns, "active", "is_active", "isactive"),
        deleted_at=pick_column(columns, "deleted_at", "deletedat", "removed_at", "removedat"),
        created_at=pick_column(columns, "created_at", "createdat", "date_create", "datecreate"),
        updated_at=pick_column(columns, "updated_at", "updatedat", "date_update", "dateupdate"),
    )

    if not mapped.id:
        return None

    return AppointmentContext(
        ref=ref,
        columns=columns,
        mapping=mapped,
        is_bootstrap=is_bootstrap,
    )


def _resolve_contexts(conn) -> list[AppointmentContext]:
    _ensure_bootstrap_table(conn)

    contexts: list[AppointmentContext] = []

    bootstrap_ref = resolve_table(conn, "app_appointments")
    if bootstrap_ref:
        bootstrap_ctx = _build_context(conn, bootstrap_ref, is_bootstrap=True)
        if bootstrap_ctx:
            contexts.append(bootstrap_ctx)

    legacy_ref = resolve_table(
        conn,
        "appointments",
        "appointment",
        "customer_appointments",
        "customerappointments",
    )
    if legacy_ref and (
        not bootstrap_ref
        or legacy_ref.schema != bootstrap_ref.schema
        or legacy_ref.table != bootstrap_ref.table
    ):
        legacy_ctx = _build_context(conn, legacy_ref, is_bootstrap=False)
        if legacy_ctx:
            contexts.append(legacy_ctx)

    return contexts


def _visibility_conditions(ctx: AppointmentContext) -> list[str]:
    conditions: list[str] = []

    if ctx.mapping.active:
        active_col = quote_ident(ctx.mapping.active)
        conditions.append(
            "COALESCE(lower(NULLIF(CAST({col} AS TEXT), '')), 'true') "
            "IN ('1', 't', 'true', 'yes', 'y')".format(col=active_col)
        )

    if ctx.mapping.deleted_at:
        deleted_col = quote_ident(ctx.mapping.deleted_at)
        conditions.append(
            "({col} IS NULL OR NULLIF(CAST({col} AS TEXT), '') IS NULL)".format(col=deleted_col)
        )

    return conditions


def _text_expr(column: str | None) -> str:
    if not column:
        return "NULL::TEXT"
    return f"CAST({quote_ident(column)} AS TEXT)"


def _date_expr(column: str | None) -> str:
    if not column:
        return "NULL::DATE"
    return f"CAST({quote_ident(column)} AS DATE)"


def _time_expr(time_column: str | None, fallback_datetime_column: str | None = None) -> str:
    if time_column:
        return f"CAST({quote_ident(time_column)} AS TIME)"
    if fallback_datetime_column:
        return f"CAST({quote_ident(fallback_datetime_column)} AS TIME)"
    return "NULL::TIME"


def _state_expr(column: str | None) -> str:
    if not column:
        return "'waiting'::TEXT"
    return f"LOWER(CAST({quote_ident(column)} AS TEXT))"


def _build_select_sql(
    ctx: AppointmentContext,
    *,
    appointment_id: str | None = None,
    company_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    states: set[str] | None = None,
    search: str | None = None,
) -> tuple[str, list]:
    clauses = _visibility_conditions(ctx)
    params: list = []

    if appointment_id:
        clauses.append(f"CAST({quote_ident(ctx.mapping.id)} AS TEXT) = %s")
        params.append(appointment_id)

    if company_id:
        if not ctx.mapping.company_id:
            clauses.append("1 = 0")
        else:
            clauses.append(f"CAST({quote_ident(ctx.mapping.company_id)} AS TEXT) = %s")
            params.append(company_id)

    if date_from:
        if not ctx.mapping.appointment_date:
            clauses.append("1 = 0")
        else:
            clauses.append(f"CAST({quote_ident(ctx.mapping.appointment_date)} AS DATE) >= %s")
            params.append(date_from)

    if date_to:
        if not ctx.mapping.appointment_date:
            clauses.append("1 = 0")
        else:
            clauses.append(f"CAST({quote_ident(ctx.mapping.appointment_date)} AS DATE) <= %s")
            params.append(date_to)

    if states:
        if not ctx.mapping.state:
            clauses.append("1 = 0")
        else:
            clauses.append(f"LOWER(CAST({quote_ident(ctx.mapping.state)} AS TEXT)) = ANY(%s)")
            params.append(list(states))

    if search:
        search_value = f"%{search.strip()}%"
        search_clauses: list[str] = []
        for col in (ctx.mapping.patient_name, ctx.mapping.patient_phone, ctx.mapping.doctor_name):
            if col:
                search_clauses.append(f"CAST({quote_ident(col)} AS TEXT) ILIKE %s")
                params.append(search_value)
        if search_clauses:
            clauses.append("(" + " OR ".join(search_clauses) + ")")

    where_sql = ""
    if clauses:
        where_sql = "WHERE " + " AND ".join(clauses)

    source_label = f"{ctx.ref.schema}.{ctx.ref.table}"

    sql = f"""
        SELECT
            {_text_expr(ctx.mapping.id)} AS id,
            {_text_expr(ctx.mapping.company_id)} AS company_id,
            {_text_expr(ctx.mapping.partner_id)} AS partner_id,
            {_text_expr(ctx.mapping.patient_name)} AS patient_name,
            {_text_expr(ctx.mapping.patient_phone)} AS patient_phone,
            {_text_expr(ctx.mapping.doctor_id)} AS doctor_id,
            {_text_expr(ctx.mapping.doctor_name)} AS doctor_name,
            {_date_expr(ctx.mapping.appointment_date)} AS appointment_date,
            {_time_expr(ctx.mapping.start_time, ctx.mapping.appointment_date)} AS start_time,
            {_time_expr(ctx.mapping.end_time)} AS end_time,
            {_state_expr(ctx.mapping.state)} AS state,
            {_text_expr(ctx.mapping.services)} AS services,
            {_text_expr(ctx.mapping.notes)} AS notes,
            {_text_expr(ctx.mapping.created_at)} AS created_at,
            {_text_expr(ctx.mapping.updated_at)} AS updated_at,
            %s::TEXT AS source_table
        FROM {ctx.ref.qualified_name}
        {where_sql}
    """
    return sql, [source_label, *params]


def _run_union_query(
    conn,
    select_parts: list[tuple[str, list]],
    *,
    offset: int,
    limit: int,
) -> tuple[int, list[dict]]:
    if not select_parts:
        return 0, []

    union_sql = " UNION ALL ".join(f"({sql})" for sql, _ in select_parts)
    params: list = []
    for _sql, sql_params in select_parts:
        params.extend(sql_params)

    count_sql = f"SELECT COUNT(*) AS total FROM ({union_sql}) AS unioned"

    order_sql = "ORDER BY appointment_date DESC NULLS LAST, start_time ASC NULLS LAST, id"
    fetch_sql = f"SELECT * FROM ({union_sql}) AS unioned {order_sql}"
    fetch_params = list(params)

    if limit == 0:
        if offset > 0:
            fetch_sql += " OFFSET %s"
            fetch_params.append(offset)
    else:
        fetch_sql += " LIMIT %s OFFSET %s"
        fetch_params.extend([limit, offset])

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(count_sql, params)
        total = int(cur.fetchone()["total"])
        if total == 0:
            return 0, []

        cur.execute(fetch_sql, fetch_params)
        rows = [dict(row) for row in cur.fetchall()]

    return total, rows


def _row_to_item(row: dict, *, include_source: bool = False) -> dict:
    state = _normalize_state_or_default(row.get("state"))
    appointment_date = row.get("appointment_date")
    start_value = row.get("start_time")
    end_value = row.get("end_time")

    item = {
        "id": str(row.get("id")),
        "companyId": row.get("company_id"),
        "partnerId": row.get("partner_id"),
        "patientName": row.get("patient_name") or "",
        "patientPhone": row.get("patient_phone"),
        "doctorId": row.get("doctor_id"),
        "doctorName": row.get("doctor_name"),
        "appointmentDate": appointment_date.isoformat() if appointment_date else None,
        "startTime": _format_time(start_value),
        "endTime": _format_time(end_value),
        "state": state,
        "services": _normalize_services(row.get("services")),
        "notes": row.get("notes"),
        "createdAt": _parse_iso_datetime(row.get("created_at")),
        "updatedAt": _parse_iso_datetime(row.get("updated_at")),
    }

    if include_source:
        item["_sourceTable"] = row.get("source_table")

    return item


def _normalize_state_or_default(value: str | None) -> str:
    if value is None:
        return "waiting"
    raw = str(value).strip().lower().replace(" ", "_")
    aliases = {
        "inprogress": "in_progress",
        "in-progress": "in_progress",
        "completed": "done",
        "complete": "done",
        "canceled": "cancel",
        "cancelled": "cancel",
    }
    raw = aliases.get(raw, raw)
    if raw in APPOINTMENT_STATES:
        return raw
    return "waiting"


def _fetch_items(
    conn,
    contexts: list[AppointmentContext],
    *,
    appointment_id: str | None = None,
    company_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    states: set[str] | None = None,
    search: str | None = None,
    offset: int,
    limit: int,
) -> tuple[int, list[dict]]:
    select_parts: list[tuple[str, list]] = []
    for ctx in contexts:
        sql, params = _build_select_sql(
            ctx,
            appointment_id=appointment_id,
            company_id=company_id,
            date_from=date_from,
            date_to=date_to,
            states=states,
            search=search,
        )
        select_parts.append((sql, params))

    return _run_union_query(conn, select_parts, offset=offset, limit=limit)


def _find_context_by_source(
    contexts: list[AppointmentContext],
    source_table: str | None,
) -> AppointmentContext | None:
    if not source_table:
        return None
    for ctx in contexts:
        if source_table == f"{ctx.ref.schema}.{ctx.ref.table}":
            return ctx
    return None


def _find_appointment_for_update(conn, contexts: list[AppointmentContext], appointment_id: str) -> tuple[AppointmentContext, dict]:
    total, rows = _fetch_items(
        conn,
        contexts,
        appointment_id=appointment_id,
        offset=0,
        limit=1,
    )
    if total == 0 or not rows:
        raise HTTPException(status_code=404, detail="Appointment not found")

    row = rows[0]
    context = _find_context_by_source(contexts, row.get("source_table"))
    if not context:
        raise HTTPException(status_code=500, detail="Could not resolve appointment source table")

    return context, _row_to_item(row, include_source=True)


def _bootstrap_context_or_503(contexts: list[AppointmentContext]) -> AppointmentContext:
    for ctx in contexts:
        if ctx.is_bootstrap:
            return ctx
    raise HTTPException(status_code=503, detail="Bootstrap appointment table is unavailable")


def _validate_transition(old_state: str, new_state: str) -> None:
    allowed = STATE_TRANSITIONS.get(old_state, {old_state})
    if new_state not in allowed:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid appointment state transition from '{old_state}' to '{new_state}'",
        )


def _apply_state_update_locked(conn, ctx: AppointmentContext, appointment_id: str, next_state: str) -> None:
    if not ctx.mapping.state:
        raise HTTPException(
            status_code=409,
            detail="Appointment state cannot be changed for this source table",
        )

    id_sql = f"CAST({quote_ident(ctx.mapping.id)} AS TEXT) = %s"
    clauses = [id_sql, *_visibility_conditions(ctx)]
    where_sql = " AND ".join(clauses)

    state_col = quote_ident(ctx.mapping.state)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            SELECT LOWER(CAST({state_col} AS TEXT)) AS state
            FROM {ctx.ref.qualified_name}
            WHERE {where_sql}
            FOR UPDATE
            """,
            (appointment_id,),
        )
        locked_row = cur.fetchone()

        if not locked_row:
            raise HTTPException(status_code=404, detail="Appointment not found")

        current_state = _normalize_state_or_default(locked_row.get("state"))
        _validate_transition(current_state, next_state)

        set_clauses = [f"{state_col} = %s"]
        params: list = [next_state]

        if ctx.mapping.updated_at:
            set_clauses.append(f"{quote_ident(ctx.mapping.updated_at)} = NOW()")

        params.append(appointment_id)

        cur.execute(
            f"""
            UPDATE {ctx.ref.qualified_name}
            SET {', '.join(set_clauses)}
            WHERE {where_sql}
            """,
            params,
        )


def _state_bucket(state: str) -> str:
    if state in {"waiting", "confirmed", "arrived"}:
        return "waiting"
    if state == "in_progress":
        return "in_progress"
    if state in {"done", "cancel"}:
        return "done"
    return "waiting"


def _date_from_query(raw_date: str | None) -> date:
    if raw_date is None or raw_date.strip() == "" or raw_date.strip().lower() == "today":
        return date.today()

    parsed = _parse_date(raw_date)
    if not parsed:
        raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD or 'today'")
    return parsed


def _start_minutes(start_time: str | None) -> int:
    parsed = _parse_time(start_time)
    if parsed is None:
        return CALENDAR_START_HOUR * 60
    return parsed.hour * 60 + parsed.minute


def _end_minutes(start_time: str | None, end_time: str | None) -> int:
    start = _start_minutes(start_time)
    parsed_end = _parse_time(end_time)
    if parsed_end is None:
        return start + CALENDAR_SLOT_MINUTES

    end = parsed_end.hour * 60 + parsed_end.minute
    if end <= start:
        return start + CALENDAR_SLOT_MINUTES
    return end


def _calendar_item(item: dict) -> dict:
    start_minute = _start_minutes(item.get("startTime"))
    end_minute = _end_minutes(item.get("startTime"), item.get("endTime"))
    slot_start = max((start_minute - (CALENDAR_START_HOUR * 60)) // CALENDAR_SLOT_MINUTES, 0)
    slot_span = max((end_minute - start_minute + CALENDAR_SLOT_MINUTES - 1) // CALENDAR_SLOT_MINUTES, 1)

    enriched = dict(item)
    enriched["startMinute"] = start_minute
    enriched["endMinute"] = end_minute
    enriched["slotStart"] = slot_start
    enriched["slotSpan"] = slot_span
    return enriched


def _list_to_safe_json(value: list[str] | None) -> str:
    if value is None:
        return "[]"
    return json.dumps([str(item).strip() for item in value if str(item).strip()])


def _parse_company_id(company_id: str | None, company: str | None) -> str | None:
    return company_id or company


@router.get("/states")
async def appointment_states():
    return [*APPOINTMENT_STATES]


@router.get("")
async def list_appointments(
    page: int | None = Query(default=None, ge=1),
    perPage: int | None = Query(default=None, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=500),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    company: str | None = Query(default=None),
    state: str | None = Query(default=None),
    q: str | None = Query(default=None),
):
    company_filter = _parse_company_id(companyId, company)

    normalized_states: set[str] | None = None
    if state:
        normalized_states = {_normalize_state_value(state)}

    resolved_offset, resolved_limit = page_window(
        page=page,
        per_page=perPage,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            contexts = _resolve_contexts(conn)
            if not contexts:
                return empty_page(resolved_offset, resolved_limit)

            total, rows = _fetch_items(
                conn,
                contexts,
                company_id=company_filter,
                date_from=dateFrom,
                date_to=dateTo,
                states=normalized_states,
                search=q,
                offset=resolved_offset,
                limit=resolved_limit,
            )
            items = [_row_to_item(row) for row in rows]

            return {
                "offset": resolved_offset,
                "limit": resolved_limit,
                "totalItems": total,
                "items": items,
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/calendar")
async def calendar_day(
    date: date = Query(...),
    companyId: str | None = Query(default=None),
    company: str | None = Query(default=None),
):
    company_filter = _parse_company_id(companyId, company)

    try:
        with get_conn() as conn:
            contexts = _resolve_contexts(conn)
            if not contexts:
                return {
                    "date": date.isoformat(),
                    "companyId": company_filter,
                    "slotMinutes": CALENDAR_SLOT_MINUTES,
                    "startHour": CALENDAR_START_HOUR,
                    "endHour": CALENDAR_END_HOUR,
                    "doctors": [],
                    "unassigned": [],
                    "totals": {"appointments": 0, "doctors": 0},
                }

            _total, rows = _fetch_items(
                conn,
                contexts,
                company_id=company_filter,
                date_from=date,
                date_to=date,
                offset=0,
                limit=0,
            )
            items = [_calendar_item(_row_to_item(row)) for row in rows]
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")

    doctors_map: dict[str, dict] = {}
    unassigned: list[dict] = []

    for item in items:
        doctor_id = item.get("doctorId") or ""
        doctor_name = item.get("doctorName") or ""
        if not doctor_id and not doctor_name:
            unassigned.append(item)
            continue

        key = f"{doctor_id}::{doctor_name}"
        group = doctors_map.get(key)
        if not group:
            group = {
                "doctorId": doctor_id or None,
                "doctorName": doctor_name or "N/A",
                "appointments": [],
            }
            doctors_map[key] = group
        group["appointments"].append(item)

    doctors = list(doctors_map.values())
    doctors.sort(key=lambda g: ((g["doctorName"] or "").lower(), g["doctorId"] or ""))

    for group in doctors:
        group["appointments"].sort(key=lambda item: (item["startMinute"], item["id"]))
        group["total"] = len(group["appointments"])

    unassigned.sort(key=lambda item: (item["startMinute"], item["id"]))

    return {
        "date": date.isoformat(),
        "companyId": company_filter,
        "slotMinutes": CALENDAR_SLOT_MINUTES,
        "startHour": CALENDAR_START_HOUR,
        "endHour": CALENDAR_END_HOUR,
        "doctors": doctors,
        "unassigned": unassigned,
        "totals": {
            "appointments": len(items),
            "doctors": len(doctors),
        },
    }


@router.get("/reception")
async def reception_feed(
    date: str | None = Query(default="today"),
    companyId: str | None = Query(default=None),
    company: str | None = Query(default=None),
):
    target_date = _date_from_query(date)
    company_filter = _parse_company_id(companyId, company)

    try:
        with get_conn() as conn:
            contexts = _resolve_contexts(conn)
            if not contexts:
                return {
                    "date": target_date.isoformat(),
                    "companyId": company_filter,
                    "groups": {"waiting": [], "in_progress": [], "done": []},
                    "totals": {"waiting": 0, "in_progress": 0, "done": 0, "all": 0},
                }

            _total, rows = _fetch_items(
                conn,
                contexts,
                company_id=company_filter,
                date_from=target_date,
                date_to=target_date,
                offset=0,
                limit=0,
            )
            items = [_row_to_item(row) for row in rows]
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")

    groups: dict[str, list[dict]] = {
        "waiting": [],
        "in_progress": [],
        "done": [],
    }

    for item in items:
        bucket = _state_bucket(item["state"])
        card = {
            "id": item["id"],
            "patientName": item["patientName"],
            "patientPhone": item["patientPhone"],
            "doctorId": item["doctorId"],
            "doctorName": item["doctorName"],
            "appointmentDate": item["appointmentDate"],
            "time": item["startTime"],
            "startTime": item["startTime"],
            "endTime": item["endTime"],
            "state": item["state"],
            "services": item["services"],
            "notes": item["notes"],
            "companyId": item["companyId"],
        }
        groups[bucket].append(card)

    for bucket in groups:
        groups[bucket].sort(key=lambda row: (_start_minutes(row.get("startTime")), row.get("id") or ""))

    return {
        "date": target_date.isoformat(),
        "companyId": company_filter,
        "groups": groups,
        "totals": {
            "waiting": len(groups["waiting"]),
            "in_progress": len(groups["in_progress"]),
            "done": len(groups["done"]),
            "all": len(items),
        },
    }


@router.get("/{appointment_id}")
async def get_appointment(appointment_id: str):
    try:
        with get_conn() as conn:
            contexts = _resolve_contexts(conn)
            if not contexts:
                raise HTTPException(status_code=404, detail="Appointment not found")

            total, rows = _fetch_items(
                conn,
                contexts,
                appointment_id=appointment_id,
                offset=0,
                limit=1,
            )
            if total == 0 or not rows:
                raise HTTPException(status_code=404, detail="Appointment not found")

            return _row_to_item(rows[0])
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_appointment(payload: AppointmentCreate):
    try:
        with get_conn() as conn:
            contexts = _resolve_contexts(conn)
            bootstrap_ctx = _bootstrap_context_or_503(contexts)

            appointment_id = str(uuid4())
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {bootstrap_ctx.ref.qualified_name} (
                        id,
                        company_id,
                        partner_id,
                        patient_name,
                        patient_phone,
                        doctor_id,
                        doctor_name,
                        appointment_date,
                        start_time,
                        end_time,
                        state,
                        services,
                        notes
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s::jsonb, %s
                    )
                    """,
                    (
                        appointment_id,
                        payload.companyId,
                        payload.partnerId,
                        payload.patientName.strip(),
                        payload.patientPhone,
                        payload.doctorId,
                        payload.doctorName,
                        payload.appointmentDate,
                        payload.startTime,
                        payload.endTime,
                        payload.state,
                        _list_to_safe_json(payload.services),
                        payload.notes,
                    ),
                )

            total, rows = _fetch_items(
                conn,
                contexts,
                appointment_id=appointment_id,
                offset=0,
                limit=1,
            )
            if total == 0 or not rows:
                raise HTTPException(status_code=500, detail="Created appointment could not be loaded")

            return _row_to_item(rows[0])
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.put("/{appointment_id}")
async def update_appointment(appointment_id: str, payload: AppointmentUpdate):
    patch = payload.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=422, detail="No fields supplied for update")

    if "state" in patch and patch["state"] is not None:
        patch["state"] = _normalize_state_value(patch["state"])

    if "endTime" in patch and patch["endTime"] is not None:
        if "startTime" in patch and patch["startTime"] is not None and patch["endTime"] <= patch["startTime"]:
            raise HTTPException(status_code=422, detail="endTime must be later than startTime")

    try:
        with get_conn() as conn:
            contexts = _resolve_contexts(conn)
            context, current = _find_appointment_for_update(conn, contexts, appointment_id)
            mapping = context.mapping

            next_start = (
                patch.get("startTime")
                if "startTime" in patch
                else _parse_time(current.get("startTime"))
            )
            next_end = (
                patch.get("endTime")
                if "endTime" in patch
                else _parse_time(current.get("endTime"))
            )
            if next_start and next_end and next_end <= next_start:
                raise HTTPException(status_code=422, detail="endTime must be later than startTime")

            set_clauses: list[str] = []
            params: list = []

            def set_if_mapped(payload_key: str, column_name: str | None):
                if payload_key not in patch or not column_name:
                    return
                set_clauses.append(f"{quote_ident(column_name)} = %s")
                params.append(patch[payload_key])

            set_if_mapped("companyId", mapping.company_id)
            set_if_mapped("partnerId", mapping.partner_id)

            if "patientName" in patch and mapping.patient_name:
                value = patch["patientName"]
                if value is not None and not str(value).strip():
                    raise HTTPException(status_code=422, detail="patientName cannot be empty")
                set_clauses.append(f"{quote_ident(mapping.patient_name)} = %s")
                params.append(value.strip() if isinstance(value, str) else value)

            set_if_mapped("patientPhone", mapping.patient_phone)
            set_if_mapped("doctorId", mapping.doctor_id)
            set_if_mapped("doctorName", mapping.doctor_name)
            set_if_mapped("notes", mapping.notes)

            if "services" in patch and mapping.services:
                services_value = patch["services"]
                if services_value is None:
                    serialized = "[]" if context.is_bootstrap else None
                else:
                    serialized = _list_to_safe_json(services_value)

                if context.is_bootstrap:
                    set_clauses.append(f"{quote_ident(mapping.services)} = %s::jsonb")
                    params.append(serialized if serialized is not None else "[]")
                else:
                    set_clauses.append(f"{quote_ident(mapping.services)} = %s")
                    params.append(serialized)

            # Date/time handling. If source has separate time columns, update separately.
            if mapping.appointment_date:
                if mapping.start_time:
                    if "appointmentDate" in patch:
                        set_clauses.append(f"{quote_ident(mapping.appointment_date)} = %s")
                        params.append(patch["appointmentDate"])
                    if "startTime" in patch:
                        set_clauses.append(f"{quote_ident(mapping.start_time)} = %s")
                        params.append(patch["startTime"])
                elif "appointmentDate" in patch or "startTime" in patch:
                    current_date = _parse_date(current.get("appointmentDate")) or date.today()
                    current_time = _parse_time(current.get("startTime")) or time(8, 0)
                    next_date = patch.get("appointmentDate") or current_date
                    next_time = patch.get("startTime") or current_time
                    set_clauses.append(f"{quote_ident(mapping.appointment_date)} = %s")
                    params.append(datetime.combine(next_date, next_time))

            if "endTime" in patch and mapping.end_time:
                set_clauses.append(f"{quote_ident(mapping.end_time)} = %s")
                params.append(patch["endTime"])

            if "state" in patch:
                if not mapping.state:
                    raise HTTPException(
                        status_code=409,
                        detail="Appointment state cannot be changed for this source table",
                    )
                current_state = _normalize_state_or_default(current.get("state"))
                next_state = _normalize_state_value(patch["state"])
                _validate_transition(current_state, next_state)
                set_clauses.append(f"{quote_ident(mapping.state)} = %s")
                params.append(next_state)

            if mapping.updated_at:
                set_clauses.append(f"{quote_ident(mapping.updated_at)} = NOW()")

            if not set_clauses:
                raise HTTPException(
                    status_code=409,
                    detail="None of the supplied fields can be updated on this source table",
                )

            id_sql = f"CAST({quote_ident(mapping.id)} AS TEXT) = %s"
            clauses = [id_sql, *_visibility_conditions(context)]
            where_sql = " AND ".join(clauses)

            params.append(appointment_id)

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {context.ref.qualified_name}
                    SET {', '.join(set_clauses)}
                    WHERE {where_sql}
                    """,
                    params,
                )
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Appointment not found")

            total, rows = _fetch_items(
                conn,
                contexts,
                appointment_id=appointment_id,
                offset=0,
                limit=1,
            )
            if total == 0 or not rows:
                raise HTTPException(status_code=404, detail="Appointment not found")

            return _row_to_item(rows[0])
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str):
    try:
        with get_conn() as conn:
            contexts = _resolve_contexts(conn)
            context, _current = _find_appointment_for_update(conn, contexts, appointment_id)
            mapping = context.mapping

            id_sql = f"CAST({quote_ident(mapping.id)} AS TEXT) = %s"
            clauses = [id_sql, *_visibility_conditions(context)]
            where_sql = " AND ".join(clauses)

            with conn.cursor() as cur:
                if mapping.deleted_at:
                    set_clauses = [f"{quote_ident(mapping.deleted_at)} = NOW()"]
                    if mapping.updated_at:
                        set_clauses.append(f"{quote_ident(mapping.updated_at)} = NOW()")
                    cur.execute(
                        f"""
                        UPDATE {context.ref.qualified_name}
                        SET {', '.join(set_clauses)}
                        WHERE {where_sql}
                        """,
                        (appointment_id,),
                    )
                elif mapping.active:
                    set_clauses = [f"{quote_ident(mapping.active)} = FALSE"]
                    if mapping.updated_at:
                        set_clauses.append(f"{quote_ident(mapping.updated_at)} = NOW()")
                    cur.execute(
                        f"""
                        UPDATE {context.ref.qualified_name}
                        SET {', '.join(set_clauses)}
                        WHERE {where_sql}
                        """,
                        (appointment_id,),
                    )
                else:
                    cur.execute(
                        f"DELETE FROM {context.ref.qualified_name} WHERE {where_sql}",
                        (appointment_id,),
                    )

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Appointment not found")

            return {"id": appointment_id, "deleted": True}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.patch("/{appointment_id}/state")
async def patch_appointment_state(appointment_id: str, payload: AppointmentStatePatch):
    try:
        with get_conn() as conn:
            contexts = _resolve_contexts(conn)
            context, _current = _find_appointment_for_update(conn, contexts, appointment_id)
            _apply_state_update_locked(conn, context, appointment_id, payload.state)

            total, rows = _fetch_items(
                conn,
                contexts,
                appointment_id=appointment_id,
                offset=0,
                limit=1,
            )
            if total == 0 or not rows:
                raise HTTPException(status_code=404, detail="Appointment not found")
            return _row_to_item(rows[0])
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
