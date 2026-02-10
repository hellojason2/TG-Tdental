"""
TDental FULL Database Sync — Pulls ALL remaining data from TDental API
═══════════════════════════════════════════════════════════════════════
This script syncs all data endpoints that the deep_sync doesn't cover.
Run this AFTER deep_sync.py completes.

Endpoints synced:
  ✅ sale_orders          (56,340 records) — Treatment order headers
  ✅ customer_receipts    (162,788 records) — Reception/check-in records
  ✅ account_payments     (53,528 records) — Payment transactions
  ✅ sale_order_payments  (49,895 records) — Payment-to-order links
  ✅ dot_khams            (83,768 records) — Exam sessions
  ✅ quotations           (75 records) — Price quotations
  ✅ stock_pickings       (58 records) — Inventory transfers
  ✅ stock_moves          (1,670 records) — Inventory movements
  ✅ commissions          (17 records) — Commission rules
  ✅ partner_categories   (12 records) — Customer tags/categories
  ✅ partner_sources      (11 records) — Lead sources
  ✅ partner_titles       (5 records) — Honorifics (Ông, Bà, etc.)
  ✅ application_users    (70 records) — System users
  ✅ application_roles    (10 records) — User roles
  ✅ res_groups           (35 records) — Permission groups
  ✅ product_categories   (1 record) — Product categories

Usage:
    python3 full_sync.py              # Sync everything
    python3 full_sync.py --quick      # Only sync small reference tables
"""

import json
import time
import sys
import os
import logging
from datetime import datetime

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

PAGE_SIZE = 200  # records per API page

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("FullSync")


# ═══════════════════════════════════════════════════════════
#  API CLIENT
# ═══════════════════════════════════════════════════════════

class TDentalAPI:
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def login(self):
        r = self.session.post(f"{TDENTAL_BASE_URL}/api/Account/Login", json={
            "userName": TDENTAL_USERNAME,
            "password": TDENTAL_PASSWORD,
            "rememberMe": False
        }, timeout=15)
        d = r.json()
        if d.get("succeeded"):
            self.token = d["token"]
            self.session.headers["Authorization"] = f"Bearer {self.token}"
            log.info(f"  ✅ Logged in as {d['user']['name']}")
            return True
        return False

    def fetch_all(self, endpoint, total_expected=None):
        """Fetch all records from a paginated endpoint"""
        all_items = []
        offset = 0
        total = total_expected or 999999

        while offset < total:
            try:
                r = self.session.get(
                    f"{TDENTAL_BASE_URL}{endpoint}",
                    params={"offset": offset, "limit": PAGE_SIZE},
                    timeout=30
                )
                if r.status_code == 401:
                    self.login()
                    continue
                if r.status_code != 200:
                    log.warning(f"  ⚠️  {endpoint} returned {r.status_code} at offset {offset}")
                    break
                data = r.json()
                if isinstance(data, dict):
                    items = data.get("items", [])
                    total = data.get("totalItems", total)
                elif isinstance(data, list):
                    items = data
                    total = len(data)
                else:
                    break

                all_items.extend(items)

                if not items or len(items) < PAGE_SIZE:
                    break
                offset += PAGE_SIZE

                if len(all_items) % 1000 < PAGE_SIZE:
                    log.info(f"    📥 {len(all_items):,}/{total:,} from {endpoint}")

            except Exception as e:
                log.error(f"  ❌ Error fetching {endpoint} at offset {offset}: {e}")
                time.sleep(2)
                continue

        return all_items, total


# ═══════════════════════════════════════════════════════════
#  SAFE VALUE HELPERS
# ═══════════════════════════════════════════════════════════

def s(val, max_len=None):
    """Safe string"""
    if val is None: return None
    v = str(val).strip()
    if v in ('', 'null', 'None'): return None
    if max_len: v = v[:max_len]
    return v

def d(val):
    """Safe decimal"""
    if val is None: return None
    try: return float(val)
    except: return None

def ts(val):
    """Safe timestamp"""
    if not val or str(val).strip() in ('', 'null', 'None'): return None
    return val

def eid(obj):
    """Extract id from object or string"""
    if obj is None: return None
    if isinstance(obj, str):
        return obj if obj and obj != '00000000-0000-0000-0000-000000000000' else None
    if isinstance(obj, dict):
        uid = obj.get('id')
        if uid and str(uid) != '00000000-0000-0000-0000-000000000000':
            return str(uid)
    return None

def en(obj):
    """Extract name from object"""
    if obj is None: return None
    if isinstance(obj, str): return obj or None
    if isinstance(obj, dict):
        n = obj.get('name')
        return str(n).strip() if n else None
    return None


# ═══════════════════════════════════════════════════════════
#  CREATE ALL TABLES
# ═══════════════════════════════════════════════════════════

def create_tables(conn):
    cur = conn.cursor()
    
    # Use autocommit temporarily for DDL
    old_autocommit = conn.autocommit
    conn.autocommit = True

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sale_orders (
        id UUID PRIMARY KEY,
        name VARCHAR(100),
        partner_id UUID,
        partner_name VARCHAR(255),
        partner_display_name VARCHAR(255),
        product_names TEXT,
        date_order TIMESTAMP,
        state VARCHAR(50),
        state_display VARCHAR(100),
        amount_total DECIMAL(15,2),
        amount_discount_total DECIMAL(15,2),
        total_paid DECIMAL(15,2),
        residual DECIMAL(15,2),
        company_name VARCHAR(255),
        doctor_name VARCHAR(255),
        sale_man_name VARCHAR(255),
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customer_receipts (
        id UUID PRIMARY KEY,
        partner_id UUID,
        partner_name VARCHAR(255),
        partner_display_name VARCHAR(255),
        partner_phone VARCHAR(50),
        state VARCHAR(50),
        date_waiting TIMESTAMP,
        date_examination TIMESTAMP,
        date_done TIMESTAMP,
        doctor_id UUID,
        doctor_name VARCHAR(255),
        reason TEXT,
        is_no_treatment BOOLEAN DEFAULT FALSE,
        is_repeat_customer BOOLEAN DEFAULT FALSE,
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS account_payments (
        id UUID PRIMARY KEY,
        name VARCHAR(100),
        partner_name VARCHAR(255),
        partner_type VARCHAR(50),
        payment_type VARCHAR(50),
        payment_date TIMESTAMP,
        amount DECIMAL(15,2),
        amount_signed DECIMAL(15,2),
        state VARCHAR(50),
        display_state VARCHAR(100),
        display_payment_type VARCHAR(100),
        journal_id UUID,
        journal_name VARCHAR(255),
        journal_type VARCHAR(50),
        communication TEXT,
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sale_order_payments (
        id UUID PRIMARY KEY,
        order_id UUID,
        order_name VARCHAR(100),
        amount DECIMAL(15,2),
        date TIMESTAMP,
        state VARCHAR(50),
        note TEXT,
        payments JSONB,
        sale_order_lines JSONB,
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dot_khams (
        id UUID PRIMARY KEY,
        name VARCHAR(100),
        partner_id UUID,
        partner_name VARCHAR(255),
        partner_ref VARCHAR(100),
        sale_order_id UUID,
        sale_order_name VARCHAR(100),
        doctor_id UUID,
        doctor_name VARCHAR(255),
        date TIMESTAMP,
        state VARCHAR(50),
        reason TEXT,
        services TEXT,
        total_amount DECIMAL(15,2),
        total_paid DECIMAL(15,2),
        total_invoices_residual DECIMAL(15,2),
        invoice_state VARCHAR(50),
        payment_state VARCHAR(50),
        note TEXT,
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quotations (
        id UUID PRIMARY KEY,
        name VARCHAR(100),
        partner_id UUID,
        partner_name VARCHAR(255),
        employee_id UUID,
        employee_name VARCHAR(255),
        date_quotation TIMESTAMP,
        date_end_quotation TIMESTAMP,
        date_applies INTEGER,
        total_amount DECIMAL(15,2),
        state VARCHAR(50),
        note TEXT,
        orders JSONB,
        payments JSONB,
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_pickings (
        id UUID PRIMARY KEY,
        name VARCHAR(100),
        partner_id UUID,
        partner_name VARCHAR(255),
        company_id UUID,
        company_name VARCHAR(255),
        date TIMESTAMP,
        date_done TIMESTAMP,
        state VARCHAR(50),
        total_amount DECIMAL(15,2),
        created_by_name VARCHAR(255),
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_moves (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        name VARCHAR(255),
        reference VARCHAR(255),
        origin VARCHAR(255),
        product_name VARCHAR(255),
        product_default_code VARCHAR(100),
        product_display_name VARCHAR(500),
        product_categ_type VARCHAR(50),
        product_qty DECIMAL(10,2),
        product_uom_qty DECIMAL(10,2),
        product_uom_name VARCHAR(100),
        price_unit DECIMAL(15,2),
        price_display DECIMAL(15,2),
        total_amount DECIMAL(15,2),
        value DECIMAL(15,2),
        uom_price DECIMAL(15,2),
        is_in BOOLEAN,
        is_out BOOLEAN,
        date TIMESTAMP,
        date_done TIMESTAMP,
        picking_id UUID,
        inventory_id UUID,
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS commissions (
        id UUID PRIMARY KEY,
        name VARCHAR(255),
        type VARCHAR(50),
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS partner_categories (
        id UUID PRIMARY KEY,
        name VARCHAR(255),
        complete_name VARCHAR(500),
        color INTEGER,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS partner_sources (
        id UUID PRIMARY KEY,
        name VARCHAR(255),
        type VARCHAR(50),
        is_collaborators BOOLEAN DEFAULT FALSE,
        is_active BOOLEAN DEFAULT TRUE,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS partner_titles (
        id UUID PRIMARY KEY,
        name VARCHAR(100),
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS application_users (
        id UUID PRIMARY KEY,
        user_name VARCHAR(255),
        name VARCHAR(255),
        phone_number VARCHAR(50),
        partner_id UUID,
        ref VARCHAR(100),
        job_id UUID,
        job_name VARCHAR(255),
        active BOOLEAN DEFAULT TRUE,
        raw_data JSONB,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS application_roles (
        id UUID PRIMARY KEY,
        name VARCHAR(255),
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS res_groups (
        id UUID PRIMARY KEY,
        name VARCHAR(255),
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS product_categories (
        id UUID PRIMARY KEY,
        name VARCHAR(255),
        complete_name VARCHAR(500),
        parent_id UUID,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── Indexes for big tables ──
    for idx in [
        "CREATE INDEX IF NOT EXISTS idx_so_partner ON sale_orders(partner_id)",
        "CREATE INDEX IF NOT EXISTS idx_so_date ON sale_orders(date_order)",
        "CREATE INDEX IF NOT EXISTS idx_so_state ON sale_orders(state)",
        "CREATE INDEX IF NOT EXISTS idx_cr_partner ON customer_receipts(partner_id)",
        "CREATE INDEX IF NOT EXISTS idx_cr_state ON customer_receipts(state)",
        "CREATE INDEX IF NOT EXISTS idx_cr_date ON customer_receipts(date_waiting)",
        "CREATE INDEX IF NOT EXISTS idx_ap_date ON account_payments(payment_date)",
        "CREATE INDEX IF NOT EXISTS idx_ap_state ON account_payments(state)",
        "CREATE INDEX IF NOT EXISTS idx_sop_order ON sale_order_payments(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_dk_partner ON dot_khams(partner_id)",
        "CREATE INDEX IF NOT EXISTS idx_dk_so ON dot_khams(sale_order_id)",
        "CREATE INDEX IF NOT EXISTS idx_dk_date ON dot_khams(date)",
        "CREATE INDEX IF NOT EXISTS idx_sm_picking ON stock_moves(picking_id)",
    ]:
        try:
            cur.execute(idx)
        except:
            pass  # index might already exist

    conn.autocommit = old_autocommit
    log.info("  ✅ All tables created")


# ═══════════════════════════════════════════════════════════
#  SYNC FUNCTIONS — one per entity
# ═══════════════════════════════════════════════════════════

def sync_table(conn, api, endpoint, table, total_expected, transform_fn):
    """Generic sync: fetch all from API, upsert to DB"""
    log.info(f"\n📦 Syncing {table} ({total_expected:,} expected)...")
    items, total = api.fetch_all(endpoint, total_expected)
    log.info(f"  📥 Fetched {len(items):,} records")

    cur = conn.cursor()
    inserted = 0
    errors = 0

    for item in items:
        try:
            sql, params = transform_fn(item)
            cur.execute(sql, params)
            inserted += 1
        except Exception as e:
            conn.rollback()
            errors += 1
            if errors <= 3:
                log.warning(f"  ⚠️  Error inserting into {table}: {e}")

        if inserted % 5000 == 0 and inserted > 0:
            conn.commit()
            log.info(f"    ✅ {inserted:,}/{len(items):,}")

    conn.commit()
    log.info(f"  ✅ {table}: {inserted:,} synced, {errors} errors")
    return inserted


def tx_sale_order(r):
    return ("""
        INSERT INTO sale_orders (id, name, partner_id, partner_name, partner_display_name,
            product_names, date_order, state, state_display,
            amount_total, amount_discount_total, total_paid, residual,
            company_name, doctor_name, sale_man_name, raw_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            state=EXCLUDED.state, total_paid=EXCLUDED.total_paid,
            residual=EXCLUDED.residual, raw_data=EXCLUDED.raw_data,
            synced_at=CURRENT_TIMESTAMP
    """, (
        r['id'], s(r.get('name'),100),
        eid(r.get('partner') or r.get('partnerId')),
        s(r.get('partnerName')),
        s(r.get('partnerDisplayName')),
        s(r.get('productNames')),
        ts(r.get('dateOrder')),
        s(r.get('state')), s(r.get('stateDisplay')),
        d(r.get('amountTotal')), d(r.get('amountDiscountTotal')),
        d(r.get('totalPaid')), d(r.get('residual')),
        s(r.get('companyName')), s(r.get('doctorName')), s(r.get('saleManName')),
        Json(r),
    ))


def tx_customer_receipt(r):
    return ("""
        INSERT INTO customer_receipts (id, partner_id, partner_name, partner_display_name,
            partner_phone, state, date_waiting, date_examination, date_done,
            doctor_id, doctor_name, reason, is_no_treatment, is_repeat_customer, raw_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            state=EXCLUDED.state, date_done=EXCLUDED.date_done,
            raw_data=EXCLUDED.raw_data, synced_at=CURRENT_TIMESTAMP
    """, (
        r['id'],
        s(r.get('partnerId')),
        s(r.get('partnerName')),
        s(r.get('partnerDisplayName')),
        s(r.get('partnerPhone'),50),
        s(r.get('state')),
        ts(r.get('dateWaiting')),
        ts(r.get('dateExamination')),
        ts(r.get('dateDone')),
        s(r.get('doctorId')),
        s(r.get('doctorName')),
        s(r.get('reason')),
        r.get('isNoTreatment', False),
        r.get('isRepeatCustomer', False),
        Json(r),
    ))


def tx_account_payment(r):
    return ("""
        INSERT INTO account_payments (id, name, partner_name, partner_type,
            payment_type, payment_date, amount, amount_signed,
            state, display_state, display_payment_type,
            journal_id, journal_name, journal_type, communication, raw_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            state=EXCLUDED.state, raw_data=EXCLUDED.raw_data,
            synced_at=CURRENT_TIMESTAMP
    """, (
        r['id'], s(r.get('name'),100),
        s(r.get('partnerName')), s(r.get('partnerType')),
        s(r.get('paymentType')),
        ts(r.get('paymentDate')),
        d(r.get('amount')), d(r.get('amountSigned')),
        s(r.get('state')), s(r.get('displayState')),
        s(r.get('displayPaymentType')),
        eid(r.get('journal')), en(r.get('journal')),
        s(r.get('journalType')),
        s(r.get('communication')),
        Json(r),
    ))


def tx_sale_order_payment(r):
    return ("""
        INSERT INTO sale_order_payments (id, order_id, order_name, amount, date,
            state, note, payments, sale_order_lines, raw_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            state=EXCLUDED.state, raw_data=EXCLUDED.raw_data,
            synced_at=CURRENT_TIMESTAMP
    """, (
        r['id'],
        s(r.get('orderId')), s(r.get('orderName'),100),
        d(r.get('amount')),
        ts(r.get('date')),
        s(r.get('state')),
        s(r.get('note')),
        Json(r.get('payments')) if r.get('payments') else None,
        Json(r.get('saleOrderLines')) if r.get('saleOrderLines') else None,
        Json(r),
    ))


def tx_dot_kham(r):
    return ("""
        INSERT INTO dot_khams (id, name, partner_id, partner_name, partner_ref,
            sale_order_id, sale_order_name,
            doctor_id, doctor_name, date, state, reason, services,
            total_amount, total_paid, total_invoices_residual,
            invoice_state, payment_state, note, raw_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            state=EXCLUDED.state, total_paid=EXCLUDED.total_paid,
            raw_data=EXCLUDED.raw_data, synced_at=CURRENT_TIMESTAMP
    """, (
        r['id'], s(r.get('name'),100),
        s(r.get('partnerId')), s(r.get('partnerName')), s(r.get('partnerRef')),
        s(r.get('saleOrderId')), s(r.get('saleOrderName')),
        s(r.get('doctorId') or r.get('doctorUserId')),
        s(r.get('doctorName')),
        ts(r.get('date')),
        s(r.get('state')),
        s(r.get('reason')),
        s(r.get('services')),
        d(r.get('totalAmount')), d(r.get('totalPaid')),
        d(r.get('totalInvoicesResidual')),
        s(r.get('invoiceState')), s(r.get('paymentState')),
        s(r.get('note')),
        Json(r),
    ))


def tx_quotation(r):
    return ("""
        INSERT INTO quotations (id, name, partner_id, partner_name,
            employee_id, employee_name, date_quotation, date_end_quotation,
            date_applies, total_amount, state, note, orders, payments, raw_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            state=EXCLUDED.state, raw_data=EXCLUDED.raw_data,
            synced_at=CURRENT_TIMESTAMP
    """, (
        r['id'], s(r.get('name'),100),
        eid(r.get('partner')), en(r.get('partner')),
        eid(r.get('employee')), en(r.get('employee')),
        ts(r.get('dateQuotation')), ts(r.get('dateEndQuotation')),
        r.get('dateApplies'),
        d(r.get('totalAmount')),
        s(r.get('state')),
        s(r.get('note')),
        Json(r.get('orders')) if r.get('orders') else None,
        Json(r.get('payments')) if r.get('payments') else None,
        Json(r),
    ))


def tx_stock_picking(r):
    return ("""
        INSERT INTO stock_pickings (id, name, partner_id, partner_name,
            company_id, company_name, date, date_done, state,
            total_amount, created_by_name, raw_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            state=EXCLUDED.state, raw_data=EXCLUDED.raw_data,
            synced_at=CURRENT_TIMESTAMP
    """, (
        r['id'], s(r.get('name'),100),
        eid(r.get('partner')), en(r.get('partner')),
        s(r.get('companyId')), s(r.get('companyName')),
        ts(r.get('date')), ts(r.get('dateDone')),
        s(r.get('state')),
        d(r.get('totalAmount')),
        s(r.get('createdByName')),
        Json(r),
    ))


def tx_stock_move(r):
    # stock_moves don't always have a UUID id, use composite
    return ("""
        INSERT INTO stock_moves (name, reference, origin,
            product_name, product_default_code, product_display_name, product_categ_type,
            product_qty, product_uom_qty, product_uom_name,
            price_unit, price_display, total_amount, value, uom_price,
            is_in, is_out, date, date_done, picking_id, inventory_id, raw_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT DO NOTHING
    """, (
        s(r.get('name')), s(r.get('reference')), s(r.get('origin')),
        s(r.get('productName')), s(r.get('productDefaultCode')),
        s(r.get('productDisplayName')), s(r.get('productCategType')),
        d(r.get('productQty')), d(r.get('productUomQty')),
        s(r.get('productUomName')),
        d(r.get('priceUnit')), d(r.get('priceDisplay')),
        d(r.get('totalAmount')), d(r.get('value')), d(r.get('uomPrice')),
        r.get('isIn'), r.get('isOut'),
        ts(r.get('date')), ts(r.get('dateDone')),
        s(r.get('pickingId')), s(r.get('inventoryId')),
        Json(r),
    ))


def tx_simple(table, r, extra_cols=None):
    """Generic simple table insert"""
    cols = {'id': r['id'], 'name': s(r.get('name'))}
    if extra_cols:
        cols.update(extra_cols)
    col_names = ', '.join(cols.keys())
    placeholders = ', '.join(['%s'] * len(cols))
    return (
        f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) "
        f"ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, synced_at=CURRENT_TIMESTAMP",
        tuple(cols.values())
    )


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def run_full_sync(quick_only=False):
    t0 = time.time()
    print("\n" + "═" * 60)
    print("  TDental FULL SYNC — All Remaining Data")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    api = TDentalAPI()
    if not api.login():
        return False

    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False

    log.info("📐 Creating tables...")
    create_tables(conn)

    total_synced = 0

    # ── Reference tables (small, always sync) ──
    log.info("\n" + "─" * 40)
    log.info("📚 Syncing reference tables...")
    log.info("─" * 40)

    for table, ep, total_exp, extra_fn in [
        ("partner_titles", "/api/PartnerTitles", 5, None),
        ("partner_sources", "/api/PartnerSources", 11,
            lambda r: {"type": s(r.get("type")), "is_collaborators": r.get("isCollaborators", False), "is_active": r.get("isActive", True)}),
        ("partner_categories", "/api/PartnerCategories", 12,
            lambda r: {"complete_name": s(r.get("completeName")), "color": r.get("color")}),
        ("application_roles", "/api/ApplicationRoles", 10, None),
        ("res_groups", "/api/ResGroups", 35, None),
        ("commissions", "/api/Commissions", 17,
            lambda r: {"type": s(r.get("type")), "raw_data": Json(r)}),
        ("product_categories", "/api/ProductCategories", 1,
            lambda r: {"complete_name": s(r.get("completeName")), "parent_id": eid(r.get("parent"))}),
    ]:
        items, _ = api.fetch_all(ep, total_exp)
        cur = conn.cursor()
        for item in items:
            extra = extra_fn(item) if extra_fn else None
            sql, params = tx_simple(table, item, extra)
            cur.execute(sql, params)
        conn.commit()
        total_synced += len(items)
        log.info(f"  ✅ {table}: {len(items)}")

    # Application users — table already exists from sync_engine with column `username`
    items, _ = api.fetch_all("/api/ApplicationUsers", 70)
    cur = conn.cursor()
    for r in items:
        cur.execute("""
            INSERT INTO application_users (id, username, name, phone_number, partner_id, ref, job_id, job_name, active, raw_data)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, active=EXCLUDED.active, raw_data=EXCLUDED.raw_data, synced_at=CURRENT_TIMESTAMP
        """, (
            r['id'], s(r.get('userName')), s(r.get('name')), s(r.get('phoneNumber')),
            s(r.get('partnerId')), s(r.get('ref')), s(r.get('jobId')), s(r.get('jobName')),
            r.get('active', True), Json(r),
        ))
    conn.commit()
    total_synced += len(items)
    log.info(f"  ✅ application_users: {len(items)}")

    if quick_only:
        log.info("\n✅ Quick sync done (reference tables only)")
        conn.close()
        return True

    # ── Big tables ──
    log.info("\n" + "─" * 40)
    log.info("🏗️  Syncing large data tables...")
    log.info("─" * 40)

    syncs = [
        ("/api/Quotations", "quotations", 75, tx_quotation),
        ("/api/StockPickings", "stock_pickings", 58, tx_stock_picking),
        ("/api/StockMoves", "stock_moves", 1670, tx_stock_move),
        ("/api/SaleOrders", "sale_orders", 56340, tx_sale_order),
        ("/api/SaleOrderPayments", "sale_order_payments", 49895, tx_sale_order_payment),
        ("/api/AccountPayments", "account_payments", 53528, tx_account_payment),
        ("/api/DotKhams", "dot_khams", 83768, tx_dot_kham),
        ("/api/CustomerReceipts", "customer_receipts", 162788, tx_customer_receipt),
    ]

    for ep, table, expected, tx_fn in syncs:
        n = sync_table(conn, api, ep, table, expected, tx_fn)
        total_synced += n

    elapsed = time.time() - t0

    # ── Summary ──
    cur = conn.cursor()
    print("\n" + "═" * 60)
    print(f"  FULL SYNC COMPLETE ({int(elapsed)}s)")
    print("═" * 60)

    tables = [
        'customers', 'sale_order_lines', 'customer_appointments',
        'sale_orders', 'customer_receipts', 'account_payments',
        'sale_order_payments', 'dot_khams', 'quotations',
        'stock_pickings', 'stock_moves', 'commissions',
        'partner_categories', 'partner_sources', 'partner_titles',
        'application_users', 'application_roles', 'res_groups',
        'product_categories', 'companies', 'employees', 'products',
    ]

    grand_total = 0
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            c = cur.fetchone()[0]
            grand_total += c
            print(f"  {t:30s} {c:>10,}")
        except:
            conn.rollback()

    print(f"  {'─'*42}")
    print(f"  {'GRAND TOTAL':30s} {grand_total:>10,}")
    print(f"\n  ✅ Done in {int(elapsed//60)}m {int(elapsed%60)}s")

    conn.close()
    return True


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    run_full_sync(quick_only=quick)
