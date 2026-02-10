"""
TDental Viewer API — Full Backend
Serves the TDental replica frontend and all data APIs.
Run: python3 viewer.py
Open: http://localhost:8899
"""
import json
import os
import decimal
import uuid
from datetime import datetime, date
from fastapi import FastAPI, Query, Path, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import uvicorn

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:PuQAsTSyIMQOGjOYzjpqnkWbDHeHJjYr@shortline.proxy.rlwy.net:16355/railway")

app = FastAPI(title="TDental Viewer")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_conn():
    return psycopg2.connect(DB_URL)


def serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(i) for i in obj]
    return obj


def paginate_query(cur, table, select_cols, where="", params=None, sort_col="id", sort_dir="DESC", page=1, per_page=20):
    params = params or []
    cur.execute(f"SELECT COUNT(*) as total FROM {table} {where}", params)
    total = cur.fetchone()["total"]
    offset = (page - 1) * per_page
    cur.execute(f"SELECT {select_cols} FROM {table} {where} ORDER BY {sort_col} {sort_dir} NULLS LAST LIMIT %s OFFSET %s",
                params + [per_page, offset])
    rows = [serialize(dict(row)) for row in cur.fetchall()]
    return {"total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page, "items": rows}


def gen_ref(cur, prefix="KH"):
    """Auto-generate next customer ref like KH000124"""
    cur.execute("SELECT ref FROM customers WHERE ref LIKE %s ORDER BY ref DESC LIMIT 1", [f"{prefix}%"])
    row = cur.fetchone()
    if row and row["ref"]:
        try:
            num = int(row["ref"].replace(prefix, "")) + 1
        except:
            num = 1
    else:
        num = 1
    return f"{prefix}{num:06d}"


# ══════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def serve_viewer():
    with open("tdental.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    with open("login.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/login")
async def login(data: dict):
    return {"success": True, "user": {"name": data.get("username", "admin"), "role": "admin"}}


# ══════════════════════════════════════════════════
# CUSTOMERS API
# ══════════════════════════════════════════════════

@app.get("/api/customers")
async def get_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
    status: str = Query(""),
    sort: str = Query("name"),
    order: str = Query("asc"),
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    where_clauses, params = [], []

    if search:
        where_clauses.append("(name ILIKE %s OR display_name ILIKE %s OR phone ILIKE %s OR email ILIKE %s OR ref ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q, q, q, q])
    if company:
        where_clauses.append("company_id = %s")
        params.append(company)
    if status:
        where_clauses.append("treatment_status = %s")
        params.append(status)

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    allowed = {"name":"name","ref":"ref","phone":"phone","company_name":"company_name",
               "created_at":"created_at","appointment_date":"appointment_date",
               "amount_treatment_total":"amount_treatment_total","birth_year":"birth_year"}
    sort_col = allowed.get(sort, "name")
    sort_dir = "DESC" if order == "desc" else "ASC"

    result = paginate_query(cur, "customers",
        "id, ref, avatar, display_name, name, phone, email, street, city_name, district_name, ward_name, "
        "birth_year, birth_month, date_of_birth, age, gender, gender_display, "
        "order_state, order_residual, total_debit, amount_treatment_total, amount_revenue_total, amount_balance, "
        "treatment_status, customer_status, customer_type, member_level, card_type, "
        "source_name, company_name, appointment_date, next_appointment_date, sale_order_date, "
        "last_treatment_complete_date, job_title, address, address_v2, active, sale_name, comment, "
        "country, marketing_staff, contact_status, potential_level, created_at, synced_at",
        where, params, sort_col, sort_dir, page, per_page)
    conn.close()
    return result


@app.get("/api/customers/{customer_id}")
async def get_customer_detail(customer_id: str = Path(...)):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM customers WHERE id = %s", [customer_id])
    customer = cur.fetchone()
    if not customer:
        conn.close()
        return {"error": "Not found"}

    # Sale orders for this customer
    sale_orders = []
    try:
        cur.execute("SELECT * FROM sale_orders WHERE partner_id = %s ORDER BY date_order DESC NULLS LAST LIMIT 50", [customer_id])
        sale_orders = [serialize(dict(r)) for r in cur.fetchall()]
    except:
        pass

    # Appointments
    appointments = []
    try:
        cur.execute("SELECT * FROM customer_appointments WHERE partner_id = %s ORDER BY date DESC NULLS LAST LIMIT 50", [customer_id])
        appointments = [serialize(dict(r)) for r in cur.fetchall()]
    except:
        pass

    conn.close()
    return serialize({"customer": dict(customer), "sale_orders": sale_orders, "appointments": appointments})


@app.post("/api/customers")
async def create_customer(data: dict):
    """Create a new customer — called by saveModalEntry('customer')"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        new_id = str(uuid.uuid4())
        ref = gen_ref(cur, "KH")
        name = data.get("name", "").strip()
        if not name:
            return JSONResponse({"message": "Vui lòng nhập họ tên"}, status_code=400)

        cur.execute("""
            INSERT INTO customers (id, ref, name, display_name, phone, email, gender, gender_display,
                date_of_birth, source_name, address, active, created_at, synced_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            new_id, ref, name, name,
            data.get("phone"),
            data.get("email"),
            data.get("gender"),
            {"male": "Nam", "female": "Nữ", "other": "Khác"}.get(data.get("gender"), ""),
            data.get("date_of_birth"),
            data.get("source_name") or data.get("source_id"),
            data.get("address"),
        ))
        conn.commit()
        return {"success": True, "id": new_id, "ref": ref, "message": f"Đã tạo khách hàng {ref}"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()


@app.put("/api/customers/{customer_id}")
async def update_customer(customer_id: str, data: dict):
    """Update a customer's basic fields"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        updates, params = [], []
        field_map = {
            "name": "name", "display_name": "display_name", "phone": "phone",
            "email": "email", "gender": "gender", "address": "address",
            "date_of_birth": "date_of_birth", "source_name": "source_name",
            "comment": "comment", "treatment_status": "treatment_status",
            "customer_status": "customer_status", "active": "active",
        }
        for json_key, db_col in field_map.items():
            if json_key in data:
                updates.append(f"{db_col} = %s")
                params.append(data[json_key])

        if not updates:
            return JSONResponse({"message": "Không có dữ liệu cập nhật"}, status_code=400)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(customer_id)
        cur.execute(f"UPDATE customers SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()
        return {"success": True, "message": "Đã cập nhật"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()


@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: str):
    """Delete a customer — called by deleteCustomer()"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM customers WHERE id = %s", [customer_id])
        conn.commit()
        return {"success": True, "message": "Đã xóa khách hàng"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()


# ══════════════════════════════════════════════════
# APPOINTMENTS API
# ══════════════════════════════════════════════════

@app.get("/api/appointments")
async def get_appointments(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
    state: str = Query(""),
    sort: str = Query("date"),
    order: str = Query("desc"),
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    where_clauses, params = [], []

    if search:
        where_clauses.append("(partner_display_name ILIKE %s OR partner_ref ILIKE %s OR partner_phone ILIKE %s OR doctor_name ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q, q, q])
    if company:
        where_clauses.append("company_id = %s")
        params.append(company)
    if state:
        where_clauses.append("state = %s")
        params.append(state)

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    allowed = {"date":"date","partner_display_name":"partner_display_name","state":"state",
               "doctor_name":"doctor_name","company_name":"company_name","time":"time"}
    sort_col = allowed.get(sort, "date")
    sort_dir = "DESC" if order == "desc" else "ASC"

    result = paginate_query(cur, "customer_appointments",
        "id, partner_id, partner_display_name, partner_ref, partner_phone, "
        "date, time, note, reason, state, appointment_type, "
        "doctor_id, doctor_name, company_id, company_name",
        where, params, sort_col, sort_dir, page, per_page)
    conn.close()
    return result


@app.get("/api/appointments/calendar")
async def get_calendar_appointments(
    date: str = Query(""),
    company: str = Query(""),
):
    """Return appointments for a specific date, suitable for calendar grid view."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    where_clauses = []
    params = []

    if date:
        where_clauses.append("date::date = %s")
        params.append(date)
    else:
        where_clauses.append("date::date = CURRENT_DATE")

    if company:
        where_clauses.append("company_id = %s")
        params.append(company)

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    cur.execute(f"""
        SELECT id, partner_id, partner_display_name, partner_ref, partner_phone,
               date, time, note, reason, state, appointment_type,
               doctor_id, doctor_name, company_id, company_name,
               COALESCE(raw_data->>'doctorName', doctor_name, 'Không xác định') as calendar_doctor,
               COALESCE((raw_data->>'timeExpected')::int, 30) as duration_minutes,
               raw_data->>'stateDisplay' as state_display,
               color
        FROM customer_appointments
        {where}
        ORDER BY date ASC
    """, params)
    rows = [serialize(dict(r)) for r in cur.fetchall()]

    # Get unique doctors for this date
    doctors = sorted(set(r.get('calendar_doctor', 'Không xác định') for r in rows))
    if not doctors:
        doctors = ['Không xác định']

    conn.close()
    return {"appointments": rows, "doctors": doctors, "date": date or str(datetime.now().date())}


@app.get("/api/appointments/states")
async def get_appointment_states():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT state, COUNT(*) as c FROM customer_appointments WHERE state IS NOT NULL GROUP BY state ORDER BY c DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.post("/api/appointments")
async def create_appointment(data: dict):
    """Create a new appointment — called by saveModalEntry('appointment') and saveModalEntry('reception')"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        new_id = str(uuid.uuid4())
        partner_id = data.get("partner_id")
        if not partner_id:
            return JSONResponse({"message": "Vui lòng chọn khách hàng"}, status_code=400)

        # Look up partner info
        cur.execute("SELECT display_name, name, ref, phone FROM customers WHERE id = %s", [str(partner_id)])
        partner = cur.fetchone()
        partner_name = partner["display_name"] or partner["name"] if partner else ""
        partner_ref = partner["ref"] if partner else ""
        partner_phone = partner["phone"] if partner else ""

        # Look up doctor name
        doctor_name = None
        doctor_id = data.get("doctor_id")
        if doctor_id:
            cur.execute("SELECT name FROM employees WHERE id = %s", [str(doctor_id)])
            doc = cur.fetchone()
            doctor_name = doc["name"] if doc else None

        # Parse date/time from the combined string the frontend sends
        date_str = data.get("date", "")
        time_str = ""
        if " " in date_str:
            parts = date_str.split(" ", 1)
            date_str = parts[0]
            time_str = parts[1]

        state = data.get("state", "confirmed")

        cur.execute("""
            INSERT INTO customer_appointments
                (id, partner_id, partner_display_name, partner_ref, partner_phone,
                 date, time, note, reason, state, appointment_type,
                 doctor_id, doctor_name, created_at, synced_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            new_id, str(partner_id), partner_name, partner_ref, partner_phone,
            date_str or None, time_str or None,
            data.get("note", ""), data.get("reason", ""),
            state, data.get("appointment_type", "appointment"),
            str(doctor_id) if doctor_id else None, doctor_name,
        ))
        conn.commit()
        return {"success": True, "id": new_id, "message": "Đã tạo lịch hẹn"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()


@app.put("/api/appointments/{appt_id}")
async def update_appointment(appt_id: str, data: dict):
    """Update appointment fields (date, time, state, doctor, etc.)"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        updates, params = [], []
        field_map = {
            "state": "state", "note": "note", "reason": "reason",
            "date": "date", "time": "time",
            "doctor_id": "doctor_id", "doctor_name": "doctor_name",
        }
        for json_key, db_col in field_map.items():
            if json_key in data:
                updates.append(f"{db_col} = %s")
                params.append(data[json_key])

        if not updates:
            return JSONResponse({"message": "Không có dữ liệu cập nhật"}, status_code=400)

        updates.append("synced_at = CURRENT_TIMESTAMP")
        params.append(appt_id)
        cur.execute(f"UPDATE customer_appointments SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()
        return {"success": True, "message": "Đã cập nhật lịch hẹn"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()


@app.put("/api/appointments/{appt_id}/state")
async def update_appointment_state(appt_id: str, data: dict):
    """Change appointment state — called by saveStatus()"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        new_state = data.get("state")
        if not new_state:
            return JSONResponse({"message": "Thiếu trạng thái mới"}, status_code=400)
        cur.execute("UPDATE customer_appointments SET state = %s, synced_at = CURRENT_TIMESTAMP WHERE id = %s",
                    [new_state, appt_id])
        conn.commit()
        return {"success": True, "message": f"Đã chuyển trạng thái sang {new_state}"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()


@app.delete("/api/appointments/{appt_id}")
async def delete_appointment(appt_id: str):
    """Delete an appointment"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM customer_appointments WHERE id = %s", [appt_id])
        conn.commit()
        return {"success": True, "message": "Đã xóa lịch hẹn"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()


# ══════════════════════════════════════════════════
# DOCTORS AUTOCOMPLETE (for modals)
# ══════════════════════════════════════════════════

@app.get("/api/doctors")
async def get_doctors(search: str = Query("")):
    """Return doctors for modal dropdowns"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    where = "WHERE is_doctor = true AND active = true"
    params = []
    if search:
        where += " AND name ILIKE %s"
        params.append(f"%{search}%")
    cur.execute(f"SELECT id, name, hr_job, company_id FROM employees {where} ORDER BY name LIMIT 50", params)
    rows = [serialize(dict(r)) for r in cur.fetchall()]
    conn.close()
    return rows


# ══════════════════════════════════════════════════
# PARTNER SOURCES (for customer creation modal)
# ══════════════════════════════════════════════════

@app.get("/api/sources")
async def get_sources():
    """Return partner sources for the 'Nguồn' dropdown"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name FROM partner_sources ORDER BY name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ══════════════════════════════════════════════════
# SALE ORDERS (TREATMENTS) API
# ══════════════════════════════════════════════════

@app.get("/api/sale-orders")
async def get_sale_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
    state: str = Query(""),
    sort: str = Query("date_order"),
    order: str = Query("desc"),
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    where_clauses, params = [], []

    if search:
        where_clauses.append("(partner_name ILIKE %s OR partner_display_name ILIKE %s OR name ILIKE %s OR doctor_name ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q, q, q])
    if company:
        where_clauses.append("company_name ILIKE %s")
        params.append(f"%{company}%")
    if state:
        where_clauses.append("state = %s")
        params.append(state)

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    allowed = {"date_order":"date_order","name":"name","partner_name":"partner_name",
               "amount_total":"amount_total","state":"state","doctor_name":"doctor_name"}
    sort_col = allowed.get(sort, "date_order")
    sort_dir = "DESC" if order == "desc" else "ASC"

    result = paginate_query(cur, "sale_orders",
        "id, name, partner_id, partner_name, partner_display_name, product_names, "
        "date_order, state, state_display, amount_total, amount_discount_total, "
        "total_paid, residual, company_name, doctor_name",
        where, params, sort_col, sort_dir, page, per_page)
    conn.close()
    return result


@app.get("/api/sale-orders/{order_id}")
async def get_sale_order_detail(order_id: str = Path(...)):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM sale_orders WHERE id = %s", [order_id])
    order = cur.fetchone()
    if not order:
        conn.close()
        return {"error": "Not found"}
    # Get lines
    lines = []
    try:
        cur.execute("SELECT * FROM sale_order_lines WHERE order_id = %s", [order_id])
        lines = [serialize(dict(r)) for r in cur.fetchall()]
    except:
        pass
    # Get payments
    payments = []
    try:
        cur.execute("SELECT * FROM sale_order_payments WHERE order_id = %s ORDER BY date DESC NULLS LAST", [order_id])
        payments = [serialize(dict(r)) for r in cur.fetchall()]
    except:
        pass
    conn.close()
    return serialize({"order": dict(order), "lines": lines, "payments": payments})


@app.get("/api/sale-orders/states/summary")
async def get_sale_order_states():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT state, state_display, COUNT(*) as c, COALESCE(SUM(amount_total),0) as total FROM sale_orders GROUP BY state, state_display ORDER BY c DESC")
    rows = [serialize(dict(r)) for r in cur.fetchall()]
    conn.close()
    return rows


# ══════════════════════════════════════════════════
# PRODUCTS API


# ══════════════════════════════════════════════════
# REPORTS API
# ══════════════════════════════════════════════════

@app.get("/api/reports/revenue")
async def get_revenue_report():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # Revenue by company from dashboard_reports
    cur.execute("SELECT * FROM dashboard_reports ORDER BY company_id")
    reports = [serialize(dict(r)) for r in cur.fetchall()]

    # Revenue by month from sale_orders
    cur.execute("""
        SELECT DATE_TRUNC('month', date_order::date) as month,
               COUNT(*) as order_count,
               COALESCE(SUM(amount_total), 0) as total_revenue,
               COALESCE(SUM(total_paid), 0) as total_paid,
               COALESCE(SUM(residual), 0) as total_residual
        FROM sale_orders
        WHERE date_order IS NOT NULL
        GROUP BY DATE_TRUNC('month', date_order::date)
        ORDER BY month DESC
        LIMIT 12
    """)
    monthly = [serialize(dict(r)) for r in cur.fetchall()]

    # Revenue by company from sale_orders
    cur.execute("""
        SELECT company_name,
               COUNT(*) as order_count,
               COALESCE(SUM(amount_total), 0) as total_revenue,
               COALESCE(SUM(total_paid), 0) as total_paid,
               COALESCE(SUM(residual), 0) as total_residual
        FROM sale_orders
        WHERE company_name IS NOT NULL
        GROUP BY company_name
        ORDER BY total_revenue DESC
    """)
    by_company = [serialize(dict(r)) for r in cur.fetchall()]

    # Top doctors by revenue
    cur.execute("""
        SELECT doctor_name,
               COUNT(*) as order_count,
               COALESCE(SUM(amount_total), 0) as total_revenue
        FROM sale_orders
        WHERE doctor_name IS NOT NULL AND doctor_name != ''
        GROUP BY doctor_name
        ORDER BY total_revenue DESC
        LIMIT 10
    """)
    top_doctors = [serialize(dict(r)) for r in cur.fetchall()]

    # Top services
    cur.execute("""
        SELECT product_name,
               COUNT(*) as usage_count,
               COALESCE(SUM(amount_total), 0) as total_revenue
        FROM sale_order_lines
        WHERE product_name IS NOT NULL
        GROUP BY product_name
        ORDER BY total_revenue DESC
        LIMIT 15
    """)
    top_services = [serialize(dict(r)) for r in cur.fetchall()]

    conn.close()
    return {"reports": reports, "monthly": monthly, "by_company": by_company,
            "top_doctors": top_doctors, "top_services": top_services}


@app.get("/api/reports/overview")
async def get_overview_report(company_id: str = Query("")):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    stats = {}

    # Resolve company_name from company_id for tables that use company_name
    company_name = ""
    if company_id:
        cur.execute("SELECT name FROM companies WHERE id = %s", [company_id])
        row = cur.fetchone()
        company_name = row["name"] if row else ""

    # Customers: filter by company_id
    cust_where, cust_params = "", []
    if company_id:
        cust_where, cust_params = "WHERE company_id = %s", [company_id]
    cur.execute(f"SELECT COUNT(*) as c FROM customers {cust_where}", cust_params)
    stats["total_customers"] = cur.fetchone()["c"]

    # Sale orders: filter by company_name
    so_where, so_params = "", []
    if company_name:
        so_where, so_params = "WHERE company_name = %s", [company_name]
    cur.execute(f"SELECT COUNT(*) as c FROM sale_orders {so_where}", so_params)
    stats["total_orders"] = cur.fetchone()["c"]
    cur.execute(f"SELECT COALESCE(SUM(amount_total),0) as s FROM sale_orders {so_where}", so_params)
    stats["total_revenue"] = float(cur.fetchone()["s"])
    cur.execute(f"SELECT COALESCE(SUM(total_paid),0) as s FROM sale_orders {so_where}", so_params)
    stats["total_paid"] = float(cur.fetchone()["s"])
    cur.execute(f"SELECT COALESCE(SUM(residual),0) as s FROM sale_orders {so_where}", so_params)
    stats["total_residual"] = float(cur.fetchone()["s"])

    # Appointments: filter by company (customers table)
    appt_where, appt_params = "", []
    if company_id:
        appt_where = "WHERE partner_id IN (SELECT id FROM customers WHERE company_id = %s)"
        appt_params = [company_id]
    cur.execute(f"SELECT COUNT(*) as c FROM customer_appointments {appt_where}", appt_params)
    stats["total_appointments"] = cur.fetchone()["c"]

    # Employees: filter by company_id
    emp_where, emp_params = "", []
    if company_id:
        emp_where, emp_params = "WHERE company_id = %s", [company_id]
    cur.execute(f"SELECT COUNT(*) as c FROM employees {emp_where}", emp_params)
    stats["total_employees"] = cur.fetchone()["c"]

    # Products: filter by company_name
    prod_where, prod_params = "", []
    if company_name:
        prod_where, prod_params = "WHERE company_name = %s", [company_name]
    cur.execute(f"SELECT COUNT(*) as c FROM products {prod_where}", prod_params)
    stats["total_products"] = cur.fetchone()["c"]

    conn.close()
    return serialize(stats)


# ══════════════════════════════════════════════════
# COMPANIES & STATS
# ══════════════════════════════════════════════════

@app.get("/api/companies")
async def get_companies():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name FROM companies ORDER BY name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/api/stats")
async def get_stats(company_id: str = Query("")):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    stats = {}

    # Resolve company_name for tables that use it
    company_name = ""
    if company_id:
        cur.execute("SELECT name FROM companies WHERE id = %s", [company_id])
        row = cur.fetchone()
        company_name = row["name"] if row else ""

    # Tables with company_id filter
    for table, col in [('customers', 'company_id'), ('employees', 'company_id')]:
        if company_id:
            cur.execute(f"SELECT COUNT(*) as c FROM {table} WHERE {col} = %s", [company_id])
        else:
            cur.execute(f"SELECT COUNT(*) as c FROM {table}")
        stats[table] = cur.fetchone()["c"]

    # Tables with company_name filter
    for table in ['products']:
        if company_name:
            cur.execute(f"SELECT COUNT(*) as c FROM {table} WHERE company_name = %s", [company_name])
        else:
            cur.execute(f"SELECT COUNT(*) as c FROM {table}")
        stats[table] = cur.fetchone()["c"]

    # Tables without company filter
    for table in ['appointments', 'application_users', 'companies']:
        cur.execute(f"SELECT COUNT(*) as c FROM {table}")
        stats[table] = cur.fetchone()["c"]

    if company_id:
        cur.execute("SELECT treatment_status, COUNT(*) as c FROM customers WHERE treatment_status IS NOT NULL AND company_id = %s GROUP BY treatment_status ORDER BY c DESC LIMIT 10", [company_id])
    else:
        cur.execute("SELECT treatment_status, COUNT(*) as c FROM customers WHERE treatment_status IS NOT NULL GROUP BY treatment_status ORDER BY c DESC LIMIT 10")
    stats["treatment_statuses"] = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT company_name, COUNT(*) as c FROM customers WHERE company_name IS NOT NULL GROUP BY company_name ORDER BY c DESC")
    stats["customers_by_company"] = [dict(r) for r in cur.fetchall()]
    conn.close()
    return serialize(stats)


# ══════════════════════════════════════════════════
# STOCK PICKINGS (Purchase / Mua hàng)
# ══════════════════════════════════════════════════

@app.get("/api/stock-pickings")
async def get_stock_pickings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    clauses, params = [], []
    if search:
        clauses.append("(name ILIKE %s OR partner_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if company:
        clauses.append("company_id = %s")
        params.append(company)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    result = paginate_query(cur, "stock_pickings",
        "id, name, partner_id, partner_name, date, date_done, state, total_amount",
        where, params, "date", "DESC", page, per_page)
    conn.close()
    return result


# ══════════════════════════════════════════════════
# PRODUCTS (Kho / Inventory)
# ══════════════════════════════════════════════════

@app.get("/api/products")
async def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    clauses, params = [], []
    if search:
        clauses.append("(name ILIKE %s OR default_code ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if company:
        # products uses company_name, resolve from companies table
        cur.execute("SELECT name FROM companies WHERE id = %s", [company])
        row = cur.fetchone()
        if row:
            clauses.append("company_name = %s")
            params.append(row["name"])
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    result = paginate_query(cur, "products",
        "id, name, default_code, categ, list_price, standard_price, type, is_labo, display_name, company_name",
        where, params, "name", "ASC", page, per_page)
    # Map categ -> category_name for frontend
    for item in result["items"]:
        categ = item.pop("categ", None)
        if isinstance(categ, dict):
            item["category_name"] = categ.get("name", "---")
        elif isinstance(categ, str):
            item["category_name"] = categ
        else:
            item["category_name"] = "---"
        item["active"] = True  # products don't have an active column
    conn.close()
    return result


# ══════════════════════════════════════════════════
# EMPLOYEES (Lương / Salary + Hoa hồng / Commission)
# ══════════════════════════════════════════════════

@app.get("/api/employees")
async def get_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    clauses, params = [], []
    if search:
        clauses.append("(name ILIKE %s OR hr_job ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if company:
        clauses.append("company_id = %s")
        params.append(company)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    result = paginate_query(cur, "employees",
        "id, name, hr_job, company_id, is_doctor, active",
        where, params, "name", "ASC", page, per_page)
    # Add company_name
    for item in result["items"]:
        cid = item.get("company_id")
        if cid:
            cur.execute("SELECT name FROM companies WHERE id = %s", [str(cid)])
            comp = cur.fetchone()
            item["company_name"] = comp["name"] if comp else "---"
        else:
            item["company_name"] = "---"
    conn.close()
    return result


# ══════════════════════════════════════════════════
# PAYMENTS (Sổ quỹ / Cashbook)
# ══════════════════════════════════════════════════

@app.get("/api/payments")
async def get_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    clauses, params = [], []
    if search:
        clauses.append("order_name ILIKE %s")
        params.append(f"%{search}%")
    if company:
        # sale_order_payments has no company col; join via order_id -> sale_orders
        cur.execute("SELECT name FROM companies WHERE id = %s", [company])
        row = cur.fetchone()
        if row:
            clauses.append("order_id IN (SELECT id FROM sale_orders WHERE company_name = %s)")
            params.append(row["name"])
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    result = paginate_query(cur, "sale_order_payments",
        "id, order_id, order_name, amount, date, state, note",
        where, params, "date", "DESC", page, per_page)
    conn.close()
    return result


# ══════════════════════════════════════════════════
# CALL CENTER (Tổng đài)
# ══════════════════════════════════════════════════

@app.get("/api/callcenter")
async def get_callcenter(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    where = "WHERE phone IS NOT NULL AND phone != ''"
    params = []
    if search:
        where += " AND (display_name ILIKE %s OR phone ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if company:
        where += " AND company_id = %s"
        params.append(company)
    result = paginate_query(cur, "customers",
        "id, ref, display_name, name, phone, appointment_date, contact_status, source_name",
        where, params, "appointment_date", "DESC", page, per_page)
    conn.close()
    return result


# ══════════════════════════════════════════════════
# CATEGORIES (Danh mục)
# ══════════════════════════════════════════════════

@app.get("/api/category-counts")
async def get_category_counts():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    result = {}
    for table in ["product_categories", "partner_categories", "partner_sources", "partner_titles"]:
        cur.execute(f"SELECT COUNT(*) as c FROM {table}")
        result[table] = cur.fetchone()["c"]
    conn.close()
    return result


@app.get("/api/categories/{table}")
async def get_category_items(table: str = Path(...)):
    allowed = ["product_categories", "partner_categories", "partner_sources", "partner_titles"]
    if table not in allowed:
        return JSONResponse({"message": "Invalid table"}, status_code=400)
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"SELECT id, name FROM {table} ORDER BY name")
    rows = [serialize(dict(r)) for r in cur.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8899))
    uvicorn.run(app, host="0.0.0.0", port=port)
