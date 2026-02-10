import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Header, Query, Path, HTTPException
from fastapi.responses import JSONResponse
from app.core.database import get_conn, get_cursor
from app.core.utils import serialize, paginate_query, gen_ref
from app.core.security import hash_password
from app.api.deps import get_current_user
import psycopg2.errors

router = APIRouter()

# ══════════════════════════════════════════════════
# USER MANAGEMENT API (admin only)
# ══════════════════════════════════════════════════

@router.get("/users")
async def list_users(authorization: str = Header(None)):
    me = get_current_user(authorization)
    if not me or me.get('role') != 'admin':
        return JSONResponse({"message": "Không có quyền truy cập"}, status_code=403)
    conn = get_conn()
    cur = get_cursor(conn)
    cur.execute("SELECT id, name, email, role, permissions, active, created_at FROM app_users ORDER BY created_at")
    rows = [serialize(dict(r)) for r in cur.fetchall()]
    conn.close()
    return {"users": rows}

@router.post("/users")
async def create_user(data: dict, authorization: str = Header(None)):
    me = get_current_user(authorization)
    if not me or me.get('role') != 'admin':
        return JSONResponse({"message": "Không có quyền truy cập"}, status_code=403)

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'viewer')
    if role not in ('admin', 'viewer'): role = 'viewer'
    permissions = data.get('permissions', {})

    if not name or not email or not password:
        return JSONResponse({"message": "Vui lòng nhập đầy đủ thông tin"}, status_code=400)

    conn = get_conn()
    cur = conn.cursor()
    try:
        user_id = 'u_' + str(uuid.uuid4())[:8]
        cur.execute("""
            INSERT INTO app_users (id, name, email, password, role, permissions, active)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, [user_id, name, email, hash_password(password), role, json.dumps(permissions)])
        conn.commit()
        return {"success": True, "id": user_id, "message": f"Đã tạo người dùng {name}"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return JSONResponse({"message": "Email đã tồn tại"}, status_code=400)
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()

@router.put("/users/role-permissions")
async def save_role_permissions(data: dict, authorization: str = Header(None)):
    me = get_current_user(authorization)
    if not me or me.get('role') != 'admin':
        return JSONResponse({"message": "Không có quyền truy cập"}, status_code=403)

    viewer_perms = data.get('viewer', [])
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Update all viewer users' permissions
        perms_json = json.dumps({p: True for p in viewer_perms})
        cur.execute("UPDATE app_users SET permissions = %s WHERE role = 'viewer'", [perms_json])
        conn.commit()
        return {"success": True, "message": "Đã lưu phân quyền"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()

@router.put("/users/{user_id}")
async def update_user(user_id: str, data: dict, authorization: str = Header(None)):
    me = get_current_user(authorization)
    if not me or me.get('role') != 'admin':
        return JSONResponse({"message": "Không có quyền truy cập"}, status_code=403)

    conn = get_conn()
    cur = conn.cursor()
    try:
        updates, params = [], []
        if 'name' in data:
            updates.append("name = %s"); params.append(data['name'])
        if 'email' in data:
            updates.append("email = %s"); params.append(data['email'].lower())
        if 'password' in data and data['password']:
            updates.append("password = %s"); params.append(hash_password(data['password']))
        if 'role' in data:
            role = data['role']
            if role not in ('admin', 'viewer'): role = 'viewer'
            updates.append("role = %s"); params.append(role)
        if 'permissions' in data:
            updates.append("permissions = %s"); params.append(json.dumps(data['permissions']))
        if 'active' in data:
            updates.append("active = %s"); params.append(data['active'])

        if not updates:
            return JSONResponse({"message": "Không có dữ liệu cập nhật"}, status_code=400)

        params.append(user_id)
        cur.execute(f"UPDATE app_users SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()
        return {"success": True, "message": "Đã cập nhật"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return JSONResponse({"message": "Email đã tồn tại"}, status_code=400)
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()

@router.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: str, authorization: str = Header(None)):
    me = get_current_user(authorization)
    if not me or me.get('role') != 'admin':
        return JSONResponse({"message": "Không có quyền truy cập"}, status_code=403)
    if me['id'] == user_id:
        return JSONResponse({"message": "Không thể xóa chính mình"}, status_code=400)

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM app_users WHERE id = %s", [user_id])
        conn.commit()
        return {"success": True, "message": "Đã xóa người dùng"}
    except Exception as e:
        conn.rollback()
        return JSONResponse({"message": str(e)}, status_code=500)
    finally:
        conn.close()

# ══════════════════════════════════════════════════
# CUSTOMERS API
# ══════════════════════════════════════════════════

@router.get("/customers")
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
    cur = get_cursor(conn)
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

@router.get("/customers/{customer_id}")
async def get_customer_detail(customer_id: str = Path(...)):
    conn = get_conn()
    cur = get_cursor(conn)
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

@router.post("/customers")
async def create_customer(data: dict):
    """Create a new customer — called by saveModalEntry('customer')"""
    conn = get_conn()
    cur = get_cursor(conn)
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

@router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, data: dict):
    """Update a customer's basic fields"""
    conn = get_conn()
    cur = get_cursor(conn)
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

@router.delete("/customers/{customer_id}")
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

@router.get("/appointments")
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
    cur = get_cursor(conn)
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

@router.get("/appointments/calendar")
async def get_calendar_appointments(
    date: str = Query(""),
    company: str = Query(""),
):
    """Return appointments for a specific date, suitable for calendar grid view."""
    conn = get_conn()
    cur = get_cursor(conn)
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

@router.get("/appointments/states")
async def get_appointment_states():
    conn = get_conn()
    cur = get_cursor(conn)
    cur.execute("SELECT state, COUNT(*) as c FROM customer_appointments WHERE state IS NOT NULL GROUP BY state ORDER BY c DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@router.post("/appointments")
async def create_appointment(data: dict):
    """Create a new appointment — called by saveModalEntry('appointment') and saveModalEntry('reception')"""
    conn = get_conn()
    cur = get_cursor(conn)
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

@router.put("/appointments/{appt_id}")
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

@router.put("/appointments/{appt_id}/state")
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

@router.delete("/appointments/{appt_id}")
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

@router.get("/doctors")
async def get_doctors(search: str = Query("")):
    """Return doctors for modal dropdowns"""
    conn = get_conn()
    cur = get_cursor(conn)
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

@router.get("/sources")
async def get_sources():
    """Return partner sources for the 'Nguồn' dropdown"""
    conn = get_conn()
    cur = get_cursor(conn)
    cur.execute("SELECT id, name FROM partner_sources ORDER BY name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ══════════════════════════════════════════════════
# SALE ORDERS (TREATMENTS) API
# ══════════════════════════════════════════════════

@router.get("/sale-orders")
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
    cur = get_cursor(conn)
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

@router.get("/sale-orders/{order_id}")
async def get_sale_order_detail(order_id: str = Path(...)):
    conn = get_conn()
    cur = get_cursor(conn)
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

@router.get("/sale-orders/states/summary")
async def get_sale_order_states():
    conn = get_conn()
    cur = get_cursor(conn)
    cur.execute("SELECT state, state_display, COUNT(*) as c, COALESCE(SUM(amount_total),0) as total FROM sale_orders GROUP BY state, state_display ORDER BY c DESC")
    rows = [serialize(dict(r)) for r in cur.fetchall()]
    conn.close()
    return rows

# ══════════════════════════════════════════════════
# PRODUCTS (Inventory / Kho) API
# ══════════════════════════════════════════════════

@router.get("/products")
async def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = get_cursor(conn)
    where_clauses, params = [], []

    if search:
        where_clauses.append("(p.name ILIKE %s OR p.default_code ILIKE %s OR p.display_name ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q, q])
    if company:
        where_clauses.append("p.company_name ILIKE %s")
        params.append(f"%{company}%")

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Count
    cur.execute(f"SELECT COUNT(*) as total FROM products p {where}", params)
    total = cur.fetchone()["total"]
    offset = (page - 1) * per_page

    cur.execute(f"""
        SELECT p.id, p.name, p.default_code, p.list_price, p.standard_price,
               p.type, p.display_name, p.company_name, p.is_labo,
               pc.name as category_name,
               TRUE as active
        FROM products p
        LEFT JOIN product_categories pc ON p.categ_id = pc.id
        {where}
        ORDER BY p.name ASC NULLS LAST
        LIMIT %s OFFSET %s
    """, params + [per_page, offset])
    rows = [serialize(dict(r)) for r in cur.fetchall()]
    conn.close()
    return {"total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page, "items": rows}

# ══════════════════════════════════════════════════
# EMPLOYEES (Salary / Commission) API
# ══════════════════════════════════════════════════

@router.get("/employees")
async def get_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = get_cursor(conn)
    where_clauses, params = [], []

    if search:
        where_clauses.append("(e.name ILIKE %s OR e.hr_job ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q])
    if company:
        where_clauses.append("e.company_id = %s")
        params.append(company)

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    cur.execute(f"SELECT COUNT(*) as total FROM employees e {where}", params)
    total = cur.fetchone()["total"]
    offset = (page - 1) * per_page

    cur.execute(f"""
        SELECT e.id, e.name, e.hr_job, e.company_id, e.is_doctor, e.active,
               c.name as company_name
        FROM employees e
        LEFT JOIN companies c ON e.company_id = c.id
        {where}
        ORDER BY e.name ASC NULLS LAST
        LIMIT %s OFFSET %s
    """, params + [per_page, offset])
    rows = [serialize(dict(r)) for r in cur.fetchall()]
    conn.close()
    return {"total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page, "items": rows}

# ══════════════════════════════════════════════════
# PAYMENTS (Cashbook / Sổ quỹ) API
# ══════════════════════════════════════════════════

@router.get("/payments")
async def get_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = get_cursor(conn)
    where_clauses, params = [], []

    if search:
        where_clauses.append("(name ILIKE %s OR partner_name ILIKE %s OR communication ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q, q])
    if company:
        where_clauses.append("journal_name ILIKE %s")
        params.append(f"%{company}%")

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    result = paginate_query(cur, "account_payments",
        "id, name, partner_name, payment_type, display_payment_type, "
        "payment_date as date, amount, amount_signed, state, display_state, "
        "journal_name as order_name, communication",
        where, params, "payment_date", "DESC", page, per_page)
    conn.close()
    return result

# ══════════════════════════════════════════════════
# STOCK PICKINGS (Purchase / Mua hàng) API
# ══════════════════════════════════════════════════

@router.get("/stock-pickings")
async def get_stock_pickings(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
    picking_type: str = Query(""),
):
    conn = get_conn()
    cur = get_cursor(conn)
    where_clauses, params = [], []

    if picking_type == "in":
        where_clauses.append("name LIKE %s")
        params.append("WH/IN%")
    elif picking_type == "out":
        where_clauses.append("name LIKE %s")
        params.append("WH/OUT%")
    if search:
        where_clauses.append("(name ILIKE %s OR partner_name ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q])
    if company:
        where_clauses.append("company_id = %s")
        params.append(company)

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    result = paginate_query(cur, "stock_pickings",
        "id, name, partner_name, company_name, date, date_done, state, total_amount, created_by_name",
        where, params, "date", "DESC", page, per_page)
    conn.close()
    return result

# ══════════════════════════════════════════════════
# STOCK MOVES SUMMARY (Nhập xuất tồn / Inventory Summary) API
# ══════════════════════════════════════════════════

@router.get("/stock-moves/summary")
async def get_stock_moves_summary(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: str = Query(""),
):
    conn = get_conn()
    cur = get_cursor(conn)
    where_clauses, params = [], []

    if search:
        where_clauses.append("(product_name ILIKE %s OR product_default_code ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q])

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Count distinct products
    cur.execute(f"SELECT COUNT(*) as total FROM (SELECT 1 FROM stock_moves {where} GROUP BY product_name, product_default_code, product_uom_name) sub", params)
    total = cur.fetchone()["total"]
    offset = (page - 1) * per_page

    cur.execute(f"""
        SELECT
            product_name, product_default_code, product_uom_name,
            SUM(CASE WHEN is_in THEN product_qty ELSE 0 END) as qty_in,
            SUM(CASE WHEN is_in THEN total_amount ELSE 0 END) as amt_in,
            SUM(CASE WHEN is_out THEN product_qty ELSE 0 END) as qty_out,
            SUM(CASE WHEN is_out THEN total_amount ELSE 0 END) as amt_out
        FROM stock_moves {where}
        GROUP BY product_name, product_default_code, product_uom_name
        ORDER BY product_default_code ASC NULLS LAST
        LIMIT %s OFFSET %s
    """, params + [per_page, offset])
    rows = [serialize(dict(r)) for r in cur.fetchall()]

    # Get totals for the footer row
    cur.execute(f"""
        SELECT
            SUM(CASE WHEN is_in THEN product_qty ELSE 0 END) as total_qty_in,
            SUM(CASE WHEN is_in THEN total_amount ELSE 0 END) as total_amt_in,
            SUM(CASE WHEN is_out THEN product_qty ELSE 0 END) as total_qty_out,
            SUM(CASE WHEN is_out THEN total_amount ELSE 0 END) as total_amt_out
        FROM stock_moves {where}
    """, params)
    totals = serialize(dict(cur.fetchone()))

    conn.close()
    return {"total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page, "items": rows, "totals": totals}

# ══════════════════════════════════════════════════
# STOCK MOVES (Lịch sử xuất-nhập / In-Out History) API
# ══════════════════════════════════════════════════

@router.get("/stock-moves")
async def get_stock_moves(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: str = Query(""),
):
    conn = get_conn()
    cur = get_cursor(conn)
    where_clauses, params = [], []

    if search:
        where_clauses.append("(product_name ILIKE %s OR product_default_code ILIKE %s OR reference ILIKE %s OR name ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q, q, q])

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    result = paginate_query(cur, "stock_moves",
        "id, name, reference, origin, product_name, product_default_code, product_uom_name, "
        "product_qty, price_unit, total_amount, is_in, is_out, date, date_done",
        where, params, "date", "DESC", page, per_page)
    conn.close()
    return result

# ══════════════════════════════════════════════════
# CALL CENTER (Customers with phone) API
# ══════════════════════════════════════════════════

@router.get("/callcenter")
async def get_callcenter(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    company: str = Query(""),
):
    conn = get_conn()
    cur = get_cursor(conn)
    where_clauses = ["phone IS NOT NULL AND phone != ''"]
    params = []

    if search:
        where_clauses.append("(name ILIKE %s OR display_name ILIKE %s OR phone ILIKE %s)")
        q = f"%{search}%"
        params.extend([q, q, q])
    if company:
        where_clauses.append("company_id = %s")
        params.append(company)

    where = "WHERE " + " AND ".join(where_clauses)

    result = paginate_query(cur, "customers",
        "id, display_name, name, phone, appointment_date, source_name, contact_status, company_name",
        where, params, "name", "ASC", page, per_page)
    conn.close()
    return result

# ══════════════════════════════════════════════════
# CATEGORIES API
# ══════════════════════════════════════════════════

@router.get("/category-counts")
async def get_category_counts():
    conn = get_conn()
    cur = get_cursor(conn)
    counts = {}
    for table in ["product_categories", "partner_categories", "partner_sources", "partner_titles"]:
        try:
            cur.execute(f"SELECT COUNT(*) as c FROM {table}")
            counts[table] = cur.fetchone()["c"]
        except:
            counts[table] = 0
    conn.close()
    return counts

@router.get("/categories/{table}")
async def get_categories(table: str = Path(...)):
    allowed = ["product_categories", "partner_categories", "partner_sources", "partner_titles"]
    if table not in allowed:
        raise HTTPException(status_code=400, detail="Invalid category table")
    conn = get_conn()
    cur = get_cursor(conn)
    cur.execute(f"SELECT id, name FROM {table} ORDER BY name")
    rows = [serialize(dict(r)) for r in cur.fetchall()]
    conn.close()
    return rows

# ══════════════════════════════════════════════════
# REPORTS API
# ══════════════════════════════════════════════════

@router.get("/reports/revenue")
async def get_revenue_report():
    conn = get_conn()
    cur = get_cursor(conn)
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

@router.get("/reports/overview")
async def get_overview_report(company_id: str = Query("")):
    conn = get_conn()
    cur = get_cursor(conn)
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
    
    conn.close()
    return stats
