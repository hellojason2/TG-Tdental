"""
TDental Deep Sync — Enriches every customer with FULL detail + treatments + appointments
══════════════════════════════════════════════════════════════════════════════════════════
This script goes beyond the list API and calls the DETAIL endpoint for each customer,
plus fetches their treatment history and appointment history.

List API:    61 fields  → already synced by sync_engine.py
Detail API:  89 fields  → THIS script fetches the missing 28 fields
+ Sale Order Lines per customer (treatment records)
+ Appointments per customer

Usage:
    python3 deep_sync.py                    # Full deep sync of all customers
    python3 deep_sync.py --workers 20       # Use 20 concurrent workers (default: 10)
    python3 deep_sync.py --limit 100        # Only sync first 100 customers (for testing)
"""

import json
import time
import sys
import os
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

try:
    import requests
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    os.system(f"{sys.executable} -m pip install requests psycopg2-binary")
    import requests
    import psycopg2
    from psycopg2.extras import Json

# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════

TDENTAL_BASE_URL = "https://tamdentist.tdental.vn"
TDENTAL_USERNAME = "dataconnect"
TDENTAL_PASSWORD = "dataconnect@"
DB_URL = "postgresql://postgres:PuQAsTSyIMQOGjOYzjpqnkWbDHeHJjYr@shortline.proxy.rlwy.net:16355/railway"

DEFAULT_WORKERS = 10
BATCH_SIZE = 50  # Commit to DB every N customers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("DeepSync")


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def safe_decimal(val):
    if val is None: return None
    try: return float(val)
    except: return None

def safe_str(val, max_len=None):
    if val is None: return None
    s = str(val).strip()
    if s == '' or s == 'null': return None
    if max_len: s = s[:max_len]
    return s

def safe_timestamp(val):
    if not val or val == 'null' or '--' in str(val): return None
    s = str(val)
    if len(s) <= 4 and s.isdigit(): return None
    return val

def extract_name(obj):
    """Extract name from nested object like {id: ..., name: 'Foo'}"""
    if obj is None: return None
    if isinstance(obj, str): return obj if obj else None
    if isinstance(obj, dict):
        name = obj.get('name')
        if name and str(name).strip(): return str(name).strip()
    return None

def extract_id(obj):
    """Extract id from nested object"""
    if obj is None: return None
    if isinstance(obj, str): return obj if obj and obj != '00000000-0000-0000-0000-000000000000' else None
    if isinstance(obj, dict):
        uid = obj.get('id')
        if uid and str(uid) != '00000000-0000-0000-0000-000000000000':
            return str(uid)
    return None


# ═══════════════════════════════════════════════════════════
#  API CLIENT (thread-safe)
# ═══════════════════════════════════════════════════════════

class TDentalClient:
    def __init__(self):
        self.base_url = TDENTAL_BASE_URL
        self.token = None
        self._lock = Lock()

    def login(self):
        log.info("🔑 Logging into TDental API...")
        s = requests.Session()
        r = s.post(f"{self.base_url}/api/Account/Login", json={
            "userName": TDENTAL_USERNAME,
            "password": TDENTAL_PASSWORD,
            "rememberMe": False
        }, timeout=15)
        d = r.json()
        if d.get("succeeded"):
            self.token = d["token"]
            log.info(f"  ✅ Login OK — {d['user']['name']}")
            return True
        log.error(f"  ❌ Login failed: {d.get('message')}")
        return False

    def get(self, path, params=None, timeout=30):
        """Thread-safe GET"""
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        try:
            r = requests.get(f"{self.base_url}{path}", params=params, headers=headers, timeout=timeout)
            if r.status_code == 401:
                with self._lock:
                    self.login()
                headers["Authorization"] = f"Bearer {self.token}"
                r = requests.get(f"{self.base_url}{path}", params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            return None
        except Exception as e:
            return None

    def get_all_pages(self, path, params=None, max_items=5000):
        """Fetch all pages from paginated endpoint"""
        all_items = []
        offset = 0
        base_params = params or {}
        while True:
            p = {**base_params, "offset": offset, "limit": 100}
            data = self.get(path, params=p)
            if not data: break
            items = data.get("items", [])
            total = data.get("totalItems", 0)
            all_items.extend(items)
            if len(all_items) >= total or len(items) == 0 or len(all_items) >= max_items:
                break
            offset += 100
        return all_items


# ═══════════════════════════════════════════════════════════
#  DATABASE — Schema upgrades
# ═══════════════════════════════════════════════════════════

def upgrade_schema(conn):
    """Add missing columns and tables for deep sync"""
    cur = conn.cursor()

    # ── Add missing columns to customers table ──
    new_columns = [
        ("title_name", "VARCHAR(100)"),
        ("title_id", "UUID"),
        ("date_created", "TIMESTAMP"),
        ("emergency_phone", "VARCHAR(50)"),
        ("health_insurance_card_number", "VARCHAR(100)"),
        ("identity_number", "VARCHAR(100)"),
        ("medical_history", "TEXT"),
        ("zalo_id", "VARCHAR(100)"),
        ("referral_user_id", "UUID"),
        ("referral_user_name", "VARCHAR(255)"),
        ("consultant_id", "UUID"),
        ("consultant_name", "VARCHAR(255)"),
        ("agent_id", "UUID"),
        ("agent_name", "VARCHAR(255)"),
        ("tax_code", "VARCHAR(100)"),
        ("personal_tax_code", "VARCHAR(100)"),
        ("weight", "DECIMAL(6,2)"),
        ("loyalty_point", "INTEGER"),
        ("barcode", "VARCHAR(200)"),
        ("fax", "VARCHAR(50)"),
        ("note", "TEXT"),
        ("is_business_invoice", "BOOLEAN DEFAULT FALSE"),
        ("receiver_email", "VARCHAR(255)"),
        ("receiver_zalo_number", "VARCHAR(100)"),
        ("personal_name", "VARCHAR(255)"),
        ("personal_address", "TEXT"),
        ("personal_identity_card", "VARCHAR(100)"),
        ("unit_name", "VARCHAR(255)"),
        ("unit_address", "TEXT"),
        ("marketing_team_name", "VARCHAR(255)"),
        ("sale_team_name", "VARCHAR(255)"),
        ("tags", "TEXT"),
        ("detail_synced", "BOOLEAN DEFAULT FALSE"),
        ("detail_synced_at", "TIMESTAMP"),
    ]

    for col_name, col_type in new_columns:
        try:
            cur.execute(f"ALTER TABLE customers ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
        except Exception:
            conn.rollback()

    conn.commit()
    log.info("  ✅ Customer table upgraded with 34 new columns")

    # ── Recreate sale_order_lines table (old one had incompatible columns) ──
    cur.execute("DROP TABLE IF EXISTS sale_order_lines CASCADE")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sale_order_lines (
        id UUID PRIMARY KEY,
        order_partner_id UUID,
        order_partner_name VARCHAR(255),
        order_partner_ref VARCHAR(100),
        order_id UUID,
        order_name VARCHAR(100),
        product_id UUID,
        product_name VARCHAR(500),
        teeth_ids JSONB,
        teeth_display VARCHAR(500),
        diagnostic VARCHAR(500),
        price_unit DECIMAL(15,2),
        product_uom_qty DECIMAL(10,2),
        amount_total DECIMAL(15,2),
        amount_paid DECIMAL(15,2),
        amount_residual DECIMAL(15,2),
        state VARCHAR(50),
        date TIMESTAMP,
        date_order TIMESTAMP,
        company_id UUID,
        company_name VARCHAR(255),
        employee_id UUID,
        employee_name VARCHAR(255),
        assistant_id UUID,
        assistant_name VARCHAR(255),
        counselor_id UUID,
        counselor_name VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ── Create customer_appointments table ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customer_appointments (
        id UUID PRIMARY KEY,
        partner_id UUID,
        partner_display_name VARCHAR(255),
        partner_ref VARCHAR(100),
        partner_phone VARCHAR(50),
        date TIMESTAMP,
        time VARCHAR(20),
        note TEXT,
        reason VARCHAR(255),
        state VARCHAR(50),
        appointment_type VARCHAR(100),
        doctor_id UUID,
        doctor_name VARCHAR(255),
        company_id UUID,
        company_name VARCHAR(255),
        created_by VARCHAR(255),
        is_remind BOOLEAN DEFAULT FALSE,
        is_remind_sms BOOLEAN DEFAULT FALSE,
        color VARCHAR(50),
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ── Indexes ──
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sol_partner ON sale_order_lines(order_partner_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sol_date ON sale_order_lines(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sol_product ON sale_order_lines(product_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ca_partner ON customer_appointments(partner_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ca_date ON customer_appointments(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ca_state ON customer_appointments(state)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_detail_synced ON customers(detail_synced)")

    conn.commit()
    log.info("  ✅ sale_order_lines + customer_appointments tables ready")


# ═══════════════════════════════════════════════════════════
#  DEEP SYNC — per customer
# ═══════════════════════════════════════════════════════════

def sync_customer_detail(client, customer_id):
    """Fetch and return full detail + treatments + appointments for one customer"""
    results = {"detail": None, "treatments": [], "appointments": []}

    # 1. Full customer detail (89 fields)
    detail = client.get(f"/api/Partners/{customer_id}")
    if detail:
        results["detail"] = detail

    # 2. Treatment history (sale order lines)
    treatments = client.get_all_pages("/api/SaleOrderLines", params={
        "partnerId": customer_id
    }, max_items=500)
    results["treatments"] = treatments

    # 3. Appointment history
    appointments = client.get_all_pages("/api/Appointments", params={
        "partnerId": customer_id
    }, max_items=500)
    results["appointments"] = appointments

    return results


def save_customer_detail(conn, customer_id, data):
    """Save enriched customer data to DB"""
    cur = conn.cursor()
    detail = data["detail"]
    new_records = 0
    updated = 0

    if detail:
        # Update customer with extra fields from detail API
        cur.execute("""
            UPDATE customers SET
                source_name = COALESCE(%s, source_name),
                company_name = COALESCE(%s, company_name),
                title_name = %s,
                title_id = %s,
                date_created = %s,
                emergency_phone = %s,
                health_insurance_card_number = %s,
                identity_number = %s,
                medical_history = %s,
                zalo_id = %s,
                referral_user_id = %s,
                referral_user_name = %s,
                consultant_id = %s,
                consultant_name = %s,
                agent_id = %s,
                agent_name = %s,
                tax_code = %s,
                personal_tax_code = %s,
                weight = %s,
                loyalty_point = %s,
                barcode = %s,
                fax = %s,
                note = %s,
                is_business_invoice = %s,
                receiver_email = %s,
                receiver_zalo_number = %s,
                personal_name = %s,
                personal_address = %s,
                personal_identity_card = %s,
                unit_name = %s,
                unit_address = %s,
                marketing_team_name = %s,
                sale_team_name = %s,
                tags = %s,
                amount_treatment_total = COALESCE(%s, amount_treatment_total),
                amount_revenue_total = COALESCE(%s, amount_revenue_total),
                amount_balance = COALESCE(%s, amount_balance),
                order_residual = COALESCE(%s, order_residual),
                total_debit = COALESCE(%s, total_debit),
                display_name = COALESCE(%s, display_name),
                detail_synced = TRUE,
                detail_synced_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            extract_name(detail.get('source')),
            safe_str(detail.get('companyName')),
            extract_name(detail.get('title')),
            extract_id(detail.get('title')),
            safe_timestamp(detail.get('dateCreated')),
            safe_str(detail.get('emergencyPhone'), 50),
            safe_str(detail.get('healthInsuranceCardNumber'), 100),
            safe_str(detail.get('identityNumber'), 100),
            safe_str(detail.get('medicalHistory')),
            safe_str(detail.get('zaloId'), 100),
            extract_id(detail.get('referralUser')) or safe_str(detail.get('referralUserId')),
            extract_name(detail.get('referralUser')),
            extract_id(detail.get('consultant')) or safe_str(detail.get('consultantId')),
            extract_name(detail.get('consultant')),
            extract_id(detail.get('agent')) or safe_str(detail.get('agentId')),
            extract_name(detail.get('agent')),
            safe_str(detail.get('taxCode'), 100),
            safe_str(detail.get('personalTaxCode'), 100),
            safe_decimal(detail.get('weight')),
            int(detail['point']) if detail.get('point') else None,
            safe_str(detail.get('barcode'), 200),
            safe_str(detail.get('fax'), 50),
            safe_str(detail.get('note')),
            detail.get('isBusinessInvoice', False),
            safe_str(detail.get('receiverEmail'), 255),
            safe_str(detail.get('receiverZaloNumber'), 100),
            safe_str(detail.get('personalName'), 255),
            safe_str(detail.get('personalAddress')),
            safe_str(detail.get('personalIdentityCard'), 100),
            safe_str(detail.get('unitName'), 255),
            safe_str(detail.get('unitAddress')),
            extract_name(detail.get('marketingTeam')),
            extract_name(detail.get('saleTeam')),
            safe_str(detail.get('tags')),
            safe_decimal(detail.get('amountTreatmentTotal')),
            safe_decimal(detail.get('amountRevenueTotal')),
            safe_decimal(detail.get('amountBalance')),
            safe_decimal(detail.get('orderResidual')),
            safe_decimal(detail.get('totalDebit')),
            safe_str(detail.get('displayName')),
            customer_id,
        ))
        updated += 1

    # Save treatments
    for t in data["treatments"]:
        if not t.get("id"):
            continue
        try:
            cur.execute("""
                INSERT INTO sale_order_lines (
                    id, order_partner_id, order_partner_name, order_partner_ref,
                    order_id, order_name, product_id, product_name,
                    teeth_ids, teeth_display, diagnostic,
                    price_unit, product_uom_qty, amount_total, amount_paid, amount_residual,
                    state, date, date_order, company_id, company_name,
                    employee_id, employee_name, assistant_id, assistant_name,
                    counselor_id, counselor_name, is_active, raw_data
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                ) ON CONFLICT (id) DO UPDATE SET
                    amount_paid = EXCLUDED.amount_paid,
                    amount_residual = EXCLUDED.amount_residual,
                    state = EXCLUDED.state,
                    raw_data = EXCLUDED.raw_data,
                    synced_at = CURRENT_TIMESTAMP
            """, (
                t["id"],
                customer_id,
                safe_str(t.get("orderPartnerName") or t.get("partnerName")),
                safe_str(t.get("orderPartnerRef") or t.get("partnerRef")),
                safe_str(t.get("orderId")),
                safe_str(t.get("orderName")),
                safe_str(t.get("productId")),
                safe_str(t.get("productName") or t.get("name")),
                Json(t.get("teethIds")) if t.get("teethIds") else None,
                safe_str(t.get("teethDisplay")),
                safe_str(t.get("diagnostic")),
                safe_decimal(t.get("priceUnit")),
                safe_decimal(t.get("productUOMQty") or t.get("productUomQty")),
                safe_decimal(t.get("amountTotal") or t.get("priceSubtotal")),
                safe_decimal(t.get("amountPaid")),
                safe_decimal(t.get("amountResidual")),
                safe_str(t.get("state")),
                safe_timestamp(t.get("date")),
                safe_timestamp(t.get("dateOrder")),
                safe_str(t.get("companyId")),
                safe_str(t.get("companyName")),
                extract_id(t.get("employee")),
                extract_name(t.get("employee")),
                extract_id(t.get("assistant")),
                extract_name(t.get("assistant")),
                extract_id(t.get("counselor")),
                extract_name(t.get("counselor")),
                t.get("isActive", True),
                Json(t),
            ))
            new_records += 1
        except Exception as e:
            conn.rollback()

    # Save appointments
    for a in data["appointments"]:
        if not a.get("id"):
            continue
        try:
            doctor = a.get("doctor")
            cur.execute("""
                INSERT INTO customer_appointments (
                    id, partner_id, partner_display_name, partner_ref, partner_phone,
                    date, time, note, reason, state, appointment_type,
                    doctor_id, doctor_name, company_id, company_name,
                    created_by, is_remind, is_remind_sms, color, raw_data
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                ) ON CONFLICT (id) DO UPDATE SET
                    state = EXCLUDED.state,
                    note = EXCLUDED.note,
                    raw_data = EXCLUDED.raw_data,
                    synced_at = CURRENT_TIMESTAMP
            """, (
                a["id"],
                customer_id,
                safe_str(a.get("partnerDisplayName") or a.get("partnerName")),
                safe_str(a.get("partnerRef")),
                safe_str(a.get("partnerPhone")),
                safe_timestamp(a.get("date")),
                safe_str(a.get("time")),
                safe_str(a.get("note")),
                safe_str(a.get("reason")),
                safe_str(a.get("state")),
                safe_str(a.get("appointmentType") or a.get("type")),
                extract_id(doctor),
                extract_name(doctor),
                safe_str(a.get("companyId")),
                safe_str(a.get("companyName")),
                safe_str(a.get("createdBy")),
                a.get("isRemind", False),
                a.get("isRemindSms", False),
                safe_str(a.get("color")),
                Json(a),
            ))
            new_records += 1
        except Exception as e:
            conn.rollback()

    return updated, new_records


# ═══════════════════════════════════════════════════════════
#  MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════

def run_deep_sync(max_workers=DEFAULT_WORKERS, limit=None, skip_synced=True):
    print("\n" + "═" * 60)
    print("  TDental DEEP SYNC — Full Customer Enrichment")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Workers: {max_workers} | Skip already synced: {skip_synced}")
    print("═" * 60)

    # Login
    client = TDentalClient()
    if not client.login():
        return False

    # Connect DB
    log.info("🗄️  Connecting to database...")
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False

    # Upgrade schema
    log.info("📐 Upgrading schema...")
    upgrade_schema(conn)

    # Get list of customer IDs to sync
    cur = conn.cursor()
    if skip_synced:
        cur.execute("SELECT id FROM customers WHERE detail_synced IS NOT TRUE ORDER BY name")
    else:
        cur.execute("SELECT id FROM customers ORDER BY name")

    customer_ids = [str(row[0]) for row in cur.fetchall()]
    total = len(customer_ids)

    if limit:
        customer_ids = customer_ids[:limit]
        log.info(f"  Limiting to {limit} customers (of {total} total)")

    log.info(f"  📋 {len(customer_ids)} customers to deep-sync")

    if not customer_ids:
        log.info("  ✅ All customers already synced!")
        conn.close()
        return True

    # Stats
    t0 = time.time()
    synced_count = 0
    total_treatments = 0
    total_appointments = 0
    errors = 0
    db_lock = Lock()

    def process_customer(cid):
        """Process one customer (runs in thread)"""
        nonlocal synced_count, total_treatments, total_appointments, errors

        try:
            data = sync_customer_detail(client, cid)
            n_treat = len(data["treatments"])
            n_appt = len(data["appointments"])

            with db_lock:
                try:
                    updated, new_recs = save_customer_detail(conn, cid, data)
                    synced_count += 1
                    total_treatments += n_treat
                    total_appointments += n_appt

                    # Commit every BATCH_SIZE
                    if synced_count % BATCH_SIZE == 0:
                        conn.commit()
                        elapsed = time.time() - t0
                        rate = synced_count / elapsed
                        eta = (len(customer_ids) - synced_count) / rate if rate > 0 else 0
                        log.info(
                            f"  ✅ {synced_count:>6}/{len(customer_ids)} "
                            f"({synced_count/len(customer_ids)*100:.1f}%) "
                            f"| {total_treatments} treatments, {total_appointments} appointments "
                            f"| {rate:.1f}/s | ETA: {int(eta//60)}m{int(eta%60)}s"
                        )
                except Exception as e:
                    conn.rollback()
                    errors += 1

        except Exception as e:
            with db_lock:
                errors += 1

    # Run with thread pool
    log.info(f"\n🚀 Starting deep sync with {max_workers} workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_customer, cid): cid for cid in customer_ids}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception:
                pass

    # Final commit
    try:
        conn.commit()
    except:
        conn.rollback()

    elapsed = time.time() - t0

    # Summary
    cur = conn.cursor()
    print(f"\n{'═' * 60}")
    print(f"  DEEP SYNC COMPLETE  ({int(elapsed)}s)")
    print(f"{'═' * 60}")

    cur.execute("SELECT COUNT(*) FROM customers WHERE detail_synced = TRUE")
    detailed = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM customers")
    total_c = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM sale_order_lines")
    total_sol = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM customer_appointments")
    total_ca = cur.fetchone()[0]

    print(f"  Customers enriched:    {detailed:>8} / {total_c}")
    print(f"  Treatment records:     {total_sol:>8}")
    print(f"  Appointment records:   {total_ca:>8}")
    print(f"  Errors:                {errors:>8}")
    print(f"  Speed:                 {synced_count/elapsed:.1f} customers/sec")
    print()

    # Show sample of newly populated fields
    cur.execute("""
        SELECT COUNT(*) FROM customers WHERE source_name IS NOT NULL AND source_name != ''
    """)
    print(f"  source_name populated: {cur.fetchone()[0]}")
    cur.execute("""
        SELECT COUNT(*) FROM customers WHERE company_name IS NOT NULL AND company_name != ''
    """)
    print(f"  company_name populated: {cur.fetchone()[0]}")
    cur.execute("""
        SELECT COUNT(*) FROM customers WHERE date_created IS NOT NULL
    """)
    print(f"  date_created populated: {cur.fetchone()[0]}")
    cur.execute("""
        SELECT COUNT(*) FROM customers WHERE amount_treatment_total IS NOT NULL AND amount_treatment_total > 0
    """)
    print(f"  amount_treatment_total > 0: {cur.fetchone()[0]}")

    conn.close()
    print(f"\n  ✅ Done!")
    return True


if __name__ == "__main__":
    workers = DEFAULT_WORKERS
    limit = None
    skip = True

    if "--workers" in sys.argv:
        idx = sys.argv.index("--workers")
        workers = int(sys.argv[idx + 1])

    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        limit = int(sys.argv[idx + 1])

    if "--all" in sys.argv:
        skip = False

    run_deep_sync(max_workers=workers, limit=limit, skip_synced=skip)
