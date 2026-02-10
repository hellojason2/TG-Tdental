"""
TDental → KOL TG Live Sync Engine
═══════════════════════════════════
Middleware that polls TDental's API and syncs data to Railway PostgreSQL.
TDental.vn stays untouched — we just read their API.

Flow:  TDental.vn → TDentalMiddle (this) → Railway DB → KOL TG

Usage:
    python3 sync_engine.py                  # Run once
    python3 sync_engine.py --daemon         # Run continuously (every 5 min)
    python3 sync_engine.py --interval 60    # Custom interval in seconds
"""

import json
import time
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

import requests
import psycopg2
from psycopg2.extras import Json
from app.core.config import settings
from app.core.database import get_conn

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════

TDENTAL_BASE_URL = "https://tamdentist.tdental.vn"
TDENTAL_USERNAME = "dataconnect"
TDENTAL_PASSWORD = "dataconnect@"

DEFAULT_SYNC_INTERVAL = 300  # 5 minutes
PAGE_SIZE = 100  # Records per API page

# ═══════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("TDentalSync")


# ═══════════════════════════════════════════════════════════
#  TDENTAL API CLIENT
# ═══════════════════════════════════════════════════════════

class TDentalClient:
    """HTTP client for TDental's REST API with JWT auth"""

    def __init__(self):
        self.base_url = TDENTAL_BASE_URL
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.company_ids: List[str] = []
        self.current_company_id: Optional[str] = None

    def login(self) -> bool:
        """Authenticate and get JWT token"""
        log.info("🔑 Logging into TDental API...")
        try:
            resp = self.session.post(f"{self.base_url}/api/Account/Login", json={
                "userName": TDENTAL_USERNAME,
                "password": TDENTAL_PASSWORD,
                "rememberMe": False
            }, timeout=15)
            data = resp.json()

            if data.get("succeeded"):
                self.token = data["token"]
                self.refresh_token = data.get("refreshToken")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                # Token expires in ~7 days based on scraped data
                self.token_expiry = datetime.now() + timedelta(days=7)
                log.info(f"  ✅ Login successful! User: {data['user']['name']}")
                return True
            else:
                log.error(f"  ❌ Login failed: {data.get('message')}")
                return False
        except Exception as e:
            log.error(f"  ❌ Login error: {e}")
            return False

    def ensure_auth(self):
        """Refresh token if expired"""
        if not self.token or (self.token_expiry and datetime.now() > self.token_expiry):
            self.login()

    def get(self, path: str, params: dict = None) -> Optional[dict]:
        """GET request with auth"""
        self.ensure_auth()
        try:
            resp = self.session.get(f"{self.base_url}{path}", params=params, timeout=30)
            if resp.status_code == 401:
                log.warning("  Token expired, re-authenticating...")
                self.login()
                resp = self.session.get(f"{self.base_url}{path}", params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            log.error(f"  GET {path} failed: {e}")
            return None

    def post(self, path: str, body: dict = None) -> Optional[Any]:
        """POST request with auth"""
        self.ensure_auth()
        try:
            resp = self.session.post(f"{self.base_url}{path}", json=body or {}, timeout=30)
            if resp.status_code == 401:
                log.warning("  Token expired, re-authenticating...")
                self.login()
                resp = self.session.post(f"{self.base_url}{path}", json=body or {}, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            log.error(f"  POST {path} failed: {e}")
            return None

    def get_paginated(self, path: str, params: dict = None, page_size: int = PAGE_SIZE) -> List[dict]:
        """Fetch all pages from a paginated endpoint"""
        all_items = []
        offset = 0
        base_params = params or {}

        while True:
            p = {**base_params, "offset": offset, "limit": page_size}
            data = self.get(path, params=p)
            if not data:
                break

            items = data.get("items", [])
            total = data.get("totalItems", 0)
            all_items.extend(items)

            log.info(f"    Fetched {len(all_items)}/{total} records from {path}")

            if len(all_items) >= total or len(items) == 0:
                break
            offset += page_size

        return all_items

    def post_paginated(self, path: str, body: dict = None, page_size: int = PAGE_SIZE) -> List[dict]:
        """Fetch all pages from a paginated POST endpoint"""
        all_items = []
        offset = 0
        base_body = body or {}

        while True:
            b = {**base_body, "offset": offset, "limit": page_size}
            data = self.post(path, body=b)
            if not data:
                break

            # Some POST endpoints return arrays directly
            if isinstance(data, list):
                all_items.extend(data)
                break  # Array responses are not paginated

            items = data.get("items", [])
            total = data.get("totalItems", 0)
            all_items.extend(items)

            if len(all_items) >= total or len(items) == 0:
                break
            offset += page_size

        return all_items

    def get_session_info(self) -> Optional[dict]:
        """Get session info including companies"""
        data = self.get("/Web/Session/GetSessionInfo")
        if data:
            companies = data.get("userCompanies", {})
            allowed = companies.get("allowedCompanies", [])
            self.company_ids = [c["id"] for c in allowed]
            current = companies.get("currentCompany", {})
            self.current_company_id = current.get("id")
            log.info(f"  📍 {len(self.company_ids)} companies, current: {current.get('name')}")
        return data


# ═══════════════════════════════════════════════════════════
#  DATABASE LAYER
# ═══════════════════════════════════════════════════════════

class SyncDatabase:
    """PostgreSQL sync with upsert support"""

    def __init__(self):
        self.conn = None

    def connect(self):
        log.info("🗄️  Connecting to Railway PostgreSQL...")
        self.conn = get_conn()
        self.conn.autocommit = False
        log.info("  ✅ Connected!")

    def close(self):
        if self.conn:
            self.conn.close()

    def ensure_schema(self):
        """Create tables if they don't exist"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'companies'
        """)
        if cur.fetchone()[0] == 0:
            log.info("  Creating schema...")
            self._create_schema(cur)
            self.conn.commit()
            log.info("  ✅ Schema ready!")
        else:
            log.info("  Schema already exists.")

    def _create_schema(self, cur):
        cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            logo TEXT,
            active BOOLEAN DEFAULT TRUE,
            is_head BOOLEAN DEFAULT FALSE,
            period_lock_date TIMESTAMP,
            medical_facility_code VARCHAR(100),
            hotline VARCHAR(50),
            phone VARCHAR(50),
            address TEXT,
            address_v2 TEXT,
            used_address_v2 BOOLEAN DEFAULT FALSE,
            tax_code VARCHAR(50),
            tax_unit_name VARCHAR(255),
            tax_unit_address TEXT,
            tax_bank_name VARCHAR(255),
            tax_bank_account VARCHAR(100),
            tax_phone VARCHAR(50),
            household_businesses JSONB,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS application_users (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            partner_id UUID,
            active BOOLEAN DEFAULT TRUE,
            phone_number VARCHAR(50),
            job_id UUID,
            job_name VARCHAR(255),
            ref VARCHAR(100),
            avatar TEXT,
            employees JSONB,
            team_members JSONB,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS customers (
            id UUID PRIMARY KEY,
            ref VARCHAR(100),
            avatar TEXT,
            display_name VARCHAR(255),
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            email VARCHAR(255),
            street TEXT,
            city_name VARCHAR(255),
            district_name VARCHAR(255),
            ward_name VARCHAR(255),
            birth_year INTEGER,
            birth_month VARCHAR(20),
            birthday VARCHAR(50),
            date_of_birth VARCHAR(50),
            age VARCHAR(50),
            gender VARCHAR(20),
            gender_display VARCHAR(50),
            order_state VARCHAR(50),
            order_residual DECIMAL(15,2) DEFAULT 0,
            total_debit DECIMAL(15,2) DEFAULT 0,
            amount_treatment_total DECIMAL(15,2) DEFAULT 0,
            amount_revenue_total DECIMAL(15,2) DEFAULT 0,
            amount_balance DECIMAL(15,2) DEFAULT 0,
            treatment_status VARCHAR(100),
            customer_status VARCHAR(100),
            customer_type VARCHAR(100),
            member_level VARCHAR(100),
            card_type VARCHAR(100),
            source_id UUID,
            source_name VARCHAR(255),
            company_id UUID,
            company_name VARCHAR(255),
            appointment_date TIMESTAMP,
            next_appointment_date TIMESTAMP,
            sale_order_date TIMESTAMP,
            last_treatment_complete_date TIMESTAMP,
            job_title VARCHAR(255),
            address TEXT,
            address_v2 TEXT,
            active BOOLEAN DEFAULT TRUE,
            user_id UUID,
            sale_name VARCHAR(255),
            comment TEXT,
            categories JSONB,
            country VARCHAR(100),
            marketing_staff VARCHAR(255),
            contact_status VARCHAR(100),
            potential_level VARCHAR(100),
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS employees (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            hr_job VARCHAR(255),
            company_id UUID,
            is_doctor BOOLEAN DEFAULT FALSE,
            active BOOLEAN DEFAULT TRUE,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id UUID PRIMARY KEY,
            partner_id UUID,
            partner_display_name VARCHAR(255),
            date TIMESTAMP,
            time VARCHAR(20),
            note TEXT,
            state VARCHAR(50),
            doctor VARCHAR(255),
            company_id UUID,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS product_categories (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            complete_name VARCHAR(500),
            parent_id UUID,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS products (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            name_no_sign VARCHAR(255),
            default_code VARCHAR(100),
            price_unit DECIMAL(15,2),
            purchase_price DECIMAL(15,2),
            standard_price DECIMAL(15,2),
            list_price DECIMAL(15,2),
            categ_id UUID,
            categ JSONB,
            type VARCHAR(50),
            type2 VARCHAR(50),
            firm VARCHAR(255),
            labo_price DECIMAL(15,2),
            is_labo BOOLEAN DEFAULT FALSE,
            display_name VARCHAR(500),
            company_name VARCHAR(255),
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS partner_categories (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            complete_name VARCHAR(500),
            color VARCHAR(50),
            type VARCHAR(50),
            is_collaborators BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS partner_sources (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(50),
            is_collaborators BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sale_order_lines (
            id UUID PRIMARY KEY,
            order_id UUID,
            product_id UUID,
            product_name VARCHAR(500),
            partner_id UUID,
            partner_name VARCHAR(255),
            price_unit DECIMAL(15,2),
            product_uom_qty DECIMAL(15,2),
            price_subtotal DECIMAL(15,2),
            state VARCHAR(50),
            date TIMESTAMP,
            company_id UUID,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS customer_receipts (
            id UUID PRIMARY KEY,
            partner_id UUID,
            partner_name VARCHAR(255),
            date_receipt TIMESTAMP,
            state VARCHAR(50),
            company_id UUID,
            amount_total DECIMAL(15,2),
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS dashboard_reports (
            id SERIAL PRIMARY KEY,
            company_id UUID,
            date_from DATE,
            date_to DATE,
            total_bank DECIMAL(15,2) DEFAULT 0,
            total_cash DECIMAL(15,2) DEFAULT 0,
            total_other DECIMAL(15,2) DEFAULT 0,
            total_amount DECIMAL(15,2) DEFAULT 0,
            total_amount_yesterday DECIMAL(15,2) DEFAULT 0,
            raw_data JSONB,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_id, date_from, date_to)
        );

        CREATE TABLE IF NOT EXISTS _sync_log (
            id SERIAL PRIMARY KEY,
            sync_type VARCHAR(100) NOT NULL,
            records_synced INTEGER DEFAULT 0,
            records_new INTEGER DEFAULT 0,
            records_updated INTEGER DEFAULT 0,
            duration_ms INTEGER,
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
        CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
        CREATE INDEX IF NOT EXISTS idx_customers_company_id ON customers(company_id);
        CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
        CREATE INDEX IF NOT EXISTS idx_customers_ref ON customers(ref);
        CREATE INDEX IF NOT EXISTS idx_customers_treatment_status ON customers(treatment_status);
        CREATE INDEX IF NOT EXISTS idx_application_users_username ON application_users(username);
        CREATE INDEX IF NOT EXISTS idx_products_default_code ON products(default_code);
        CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
        CREATE INDEX IF NOT EXISTS idx_appointments_partner_id ON appointments(partner_id);
        CREATE INDEX IF NOT EXISTS idx_sale_order_lines_date ON sale_order_lines(date);
        CREATE INDEX IF NOT EXISTS idx_employees_company_id ON employees(company_id);
        """)

    def upsert_record(self, table: str, record: dict, id_field: str = "id"):
        """Upsert a single record — insert or update on conflict"""
        cur = self.conn.cursor()
        cols = list(record.keys())
        vals = list(record.values())
        placeholders = ", ".join(["%s"] * len(cols))
        col_names = ", ".join(cols)

        # Build update clause (exclude id)
        update_cols = [c for c in cols if c != id_field]
        update_clause = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])

        sql = f"""
            INSERT INTO {table} ({col_names})
            VALUES ({placeholders})
            ON CONFLICT ({id_field}) DO UPDATE SET {update_clause}, synced_at = CURRENT_TIMESTAMP
        """
        cur.execute(sql, vals)

    def log_sync(self, sync_type: str, synced: int, new: int, updated: int, duration_ms: int, status="success", error=None):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO _sync_log (sync_type, records_synced, records_new, records_updated, duration_ms, status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (sync_type, synced, new, updated, duration_ms, status, error))
        self.conn.commit()


# ═══════════════════════════════════════════════════════════
#  SYNC FUNCTIONS (one per entity)
# ═══════════════════════════════════════════════════════════

def safe_decimal(val):
    if val is None: return None
    try: return float(val)
    except: return None

def safe_timestamp(val):
    if not val or val == 'null' or '--' in str(val): return None
    s = str(val)
    if len(s) <= 4 and s.isdigit(): return None
    return val


def sync_companies(client: TDentalClient, db: SyncDatabase):
    """Sync all companies/locations"""
    t0 = time.time()
    items = client.get_paginated("/api/Companies", params={"active": "true"})
    count = 0
    for item in items:
        db.upsert_record("companies", {
            "id": item["id"], "name": item.get("name"),
            "logo": item.get("logo"), "active": item.get("active", True),
            "is_head": item.get("isHead", False),
            "period_lock_date": safe_timestamp(item.get("periodLockDate")),
            "medical_facility_code": item.get("medicalFacilityCode"),
            "hotline": item.get("hotline"), "phone": item.get("phone"),
            "address": item.get("address"), "address_v2": item.get("addressV2"),
            "used_address_v2": item.get("usedAddressV2", False),
            "tax_code": item.get("taxCode"), "tax_unit_name": item.get("taxUnitName"),
            "tax_unit_address": item.get("taxUnitAddress"),
            "tax_bank_name": item.get("taxBankName"),
            "tax_bank_account": item.get("taxBankAccount"),
            "tax_phone": item.get("taxPhone"),
            "household_businesses": Json(item.get("householdBusinesses")) if item.get("householdBusinesses") else None,
            "raw_data": Json(item),
        })
        count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("companies", count, count, 0, ms)
    log.info(f"  ✅ Companies: {count} synced ({ms}ms)")


def sync_application_users(client: TDentalClient, db: SyncDatabase):
    """Sync all application users"""
    t0 = time.time()
    items = client.get_paginated("/api/ApplicationUsers")
    count = 0
    for item in items:
        db.upsert_record("application_users", {
            "id": item["id"], "name": item.get("name"),
            "username": item.get("userName", ""),
            "partner_id": item.get("partnerId"),
            "active": item.get("active", True),
            "phone_number": item.get("phoneNumber"),
            "job_id": item.get("jobId"), "job_name": item.get("jobName"),
            "ref": item.get("ref"), "avatar": item.get("avatar"),
            "employees": Json(item.get("employees")) if item.get("employees") else None,
            "team_members": Json(item.get("teamMembers")) if item.get("teamMembers") else None,
            "raw_data": Json(item),
        })
        count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("application_users", count, count, 0, ms)
    log.info(f"  ✅ Users: {count} synced ({ms}ms)")


def sync_customers(client: TDentalClient, db: SyncDatabase):
    """Sync ALL customers with full pagination"""
    t0 = time.time()
    items = client.get_paginated("/api/Partners/GetPagedPartnersCustomer", page_size=200)
    count = 0
    for item in items:
        db.upsert_record("customers", {
            "id": item["id"], "ref": item.get("ref"),
            "avatar": item.get("avatar"),
            "display_name": item.get("displayName"),
            "name": item.get("name", ""),
            "phone": item.get("phone"), "email": item.get("email"),
            "street": item.get("street"),
            "city_name": item.get("cityName"),
            "district_name": item.get("districtName"),
            "ward_name": item.get("wardName"),
            "birth_year": item.get("birthYear"),
            "birth_month": item.get("birthMonth"),
            "birthday": item.get("birthday"),
            "date_of_birth": str(item["dateOfBirth"]) if item.get("dateOfBirth") else None,
            "age": item.get("age"), "gender": item.get("gender"),
            "gender_display": item.get("genderDisplay"),
            "order_state": item.get("orderState"),
            "order_residual": safe_decimal(item.get("orderResidual")),
            "total_debit": safe_decimal(item.get("totalDebit")),
            "amount_treatment_total": safe_decimal(item.get("amountTreatmentTotal")),
            "amount_revenue_total": safe_decimal(item.get("amountRevenueTotal")),
            "amount_balance": safe_decimal(item.get("amountBalance")),
            "treatment_status": item.get("treatmentStatus"),
            "customer_status": item.get("customerStatus"),
            "customer_type": item.get("customerType"),
            "member_level": item.get("memberLevel"),
            "card_type": item.get("cardType"),
            "source_id": item.get("sourceId"),
            "source_name": item.get("sourceName"),
            "company_id": item.get("companyId"),
            "company_name": item.get("companyName"),
            "appointment_date": safe_timestamp(item.get("appointmentDate")),
            "next_appointment_date": safe_timestamp(item.get("nextAppointmentDate")),
            "sale_order_date": safe_timestamp(item.get("saleOrderDate")),
            "last_treatment_complete_date": safe_timestamp(item.get("lastTreatmentCompleteDate")),
            "job_title": item.get("jobTitle"),
            "address": item.get("address"), "address_v2": item.get("addressV2"),
            "active": item.get("active", True),
            "user_id": item.get("userId"),
            "sale_name": item.get("saleName"),
            "comment": item.get("comment"),
            "categories": Json(item.get("categories")) if item.get("categories") else None,
            "country": item.get("country"),
            "marketing_staff": item.get("marketingStaff"),
            "contact_status": item.get("contactStatus"),
            "potential_level": item.get("potentialLevel"),
            "raw_data": Json(item),
        })
        count += 1
        if count % 500 == 0:
            db.conn.commit()
            log.info(f"    Committed {count} customers...")
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("customers", count, count, 0, ms)
    log.info(f"  ✅ Customers: {count} synced ({ms}ms)")


def sync_employees(client: TDentalClient, db: SyncDatabase):
    """Sync employees for all companies"""
    t0 = time.time()
    count = 0
    for company_id in client.company_ids:
        items = client.get_paginated("/api/Employees", params={
            "active": "true", "companyId": company_id
        })
        for item in items:
            db.upsert_record("employees", {
                "id": item["id"],
                "name": item.get("name"),
                "hr_job": item.get("hrJob") if isinstance(item.get("hrJob"), str) else (item.get("hrJob", {}) or {}).get("name"),
                "company_id": company_id,
                "is_doctor": item.get("isDoctor", False),
                "active": item.get("active", True),
                "raw_data": Json(item),
            })
            count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("employees", count, count, 0, ms)
    log.info(f"  ✅ Employees: {count} synced ({ms}ms)")


def sync_appointments(client: TDentalClient, db: SyncDatabase):
    """Sync today's appointments for all companies"""
    t0 = time.time()
    today = datetime.now().strftime("%Y-%m-%d")
    count = 0
    for company_id in client.company_ids:
        items = client.get_paginated("/api/Appointments", params={
            "dateTimeFrom": today, "dateTimeTo": today,
            "companyId": company_id
        })
        for item in items:
            db.upsert_record("appointments", {
                "id": item["id"],
                "partner_id": item.get("partnerId"),
                "partner_display_name": item.get("partnerDisplayName"),
                "date": safe_timestamp(item.get("date")),
                "time": item.get("time"),
                "note": item.get("note"),
                "state": item.get("state"),
                "doctor": item.get("doctor") if isinstance(item.get("doctor"), str) else (item.get("doctor", {}) or {}).get("name"),
                "company_id": company_id,
                "raw_data": Json(item),
            })
            count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("appointments", count, count, 0, ms)
    log.info(f"  ✅ Appointments: {count} synced ({ms}ms)")


def sync_products(client: TDentalClient, db: SyncDatabase):
    """Sync all products/services"""
    t0 = time.time()
    items = client.post_paginated("/api/products/autocomplete2", body={
        "type2": "service", "search": ""
    })
    count = 0
    for item in items:
        db.upsert_record("products", {
            "id": item["id"], "name": item.get("name", ""),
            "name_no_sign": item.get("nameNoSign"),
            "default_code": item.get("defaultCode"),
            "price_unit": safe_decimal(item.get("priceUnit")),
            "purchase_price": safe_decimal(item.get("purchasePrice")),
            "standard_price": safe_decimal(item.get("standardPrice")),
            "list_price": safe_decimal(item.get("listPrice")),
            "categ_id": item.get("categId"),
            "categ": Json(item.get("categ")) if item.get("categ") else None,
            "type": item.get("type"), "type2": item.get("type2"),
            "firm": item.get("firm"),
            "labo_price": safe_decimal(item.get("laboPrice")),
            "is_labo": item.get("isLabo", False),
            "display_name": item.get("displayName"),
            "company_name": item.get("companyName"),
            "raw_data": Json(item),
        })
        count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("products", count, count, 0, ms)
    log.info(f"  ✅ Products: {count} synced ({ms}ms)")


def sync_product_categories(client: TDentalClient, db: SyncDatabase):
    t0 = time.time()
    items = client.get_paginated("/api/productcategories", params={"type": "service"})
    count = 0
    for item in items:
        db.upsert_record("product_categories", {
            "id": item["id"], "name": item.get("name", ""),
            "complete_name": item.get("completeName"),
            "parent_id": item.get("parentId"),
            "raw_data": Json(item),
        })
        count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("product_categories", count, count, 0, ms)
    log.info(f"  ✅ Product Categories: {count} synced ({ms}ms)")


def sync_partner_categories(client: TDentalClient, db: SyncDatabase):
    t0 = time.time()
    items = client.post_paginated("/api/Partnercategories/Autocomplete", body={})
    count = 0
    for item in items:
        db.upsert_record("partner_categories", {
            "id": item["id"], "name": item.get("name", ""),
            "complete_name": item.get("completeName"),
            "color": str(item.get("color", "")),
            "type": item.get("type"),
            "is_collaborators": item.get("isCollaborators", False),
            "is_active": item.get("isActive", True),
            "raw_data": Json(item),
        })
        count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("partner_categories", count, count, 0, ms)
    log.info(f"  ✅ Partner Categories: {count} synced ({ms}ms)")


def sync_partner_sources(client: TDentalClient, db: SyncDatabase):
    t0 = time.time()
    items = client.post_paginated("/api/PartnerSources/Autocomplete", body={"isActive": True})
    count = 0
    for item in items:
        db.upsert_record("partner_sources", {
            "id": item["id"], "name": item.get("name", ""),
            "type": item.get("type"),
            "is_collaborators": item.get("isCollaborators", False),
            "is_active": item.get("isActive", True),
            "raw_data": Json(item),
        })
        count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("partner_sources", count, count, 0, ms)
    log.info(f"  ✅ Partner Sources: {count} synced ({ms}ms)")


def sync_dashboard(client: TDentalClient, db: SyncDatabase):
    """Sync today's dashboard summary for all companies"""
    t0 = time.time()
    today = datetime.now().strftime("%Y-%m-%d")
    count = 0
    for company_id in client.company_ids:
        data = client.post("/api/DashboardReports/GetSumary", body={
            "companyId": company_id,
            "dateFrom": today,
            "dateTo": today
        })
        if data:
            cur = db.conn.cursor()
            cur.execute("""
                INSERT INTO dashboard_reports (company_id, date_from, date_to,
                    total_bank, total_cash, total_other, total_amount, total_amount_yesterday, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (company_id, date_from, date_to) DO UPDATE SET
                    total_bank = EXCLUDED.total_bank,
                    total_cash = EXCLUDED.total_cash,
                    total_other = EXCLUDED.total_other,
                    total_amount = EXCLUDED.total_amount,
                    total_amount_yesterday = EXCLUDED.total_amount_yesterday,
                    raw_data = EXCLUDED.raw_data,
                    synced_at = CURRENT_TIMESTAMP
            """, (
                company_id, today, today,
                safe_decimal(data.get("totalBank")),
                safe_decimal(data.get("totalCash")),
                safe_decimal(data.get("totalOther")),
                safe_decimal(data.get("totalAmount")),
                safe_decimal(data.get("totalAmountYesterday")),
                Json(data),
            ))
            count += 1
    db.conn.commit()
    ms = int((time.time() - t0) * 1000)
    db.log_sync("dashboard_reports", count, count, 0, ms)
    log.info(f"  ✅ Dashboard: {count} company reports synced ({ms}ms)")


# ═══════════════════════════════════════════════════════════
#  MAIN SYNC ORCHESTRATOR
# ═══════════════════════════════════════════════════════════

def run_full_sync():
    """Run a complete sync of all TDental data"""
    print("\n" + "═" * 60)
    print("  TDental → KOL TG  |  LIVE SYNC")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    client = TDentalClient()
    db = SyncDatabase()

    try:
        # 1. Login
        if not client.login():
            log.error("Cannot proceed without auth!")
            return False

        # 2. Get session info (company list)
        client.get_session_info()

        # 3. Connect DB
        db.connect()
        db.ensure_schema()

        # 4. Sync all entities
        t0 = time.time()

        log.info("\n📦 Syncing reference data...")
        sync_companies(client, db)
        sync_product_categories(client, db)
        sync_partner_categories(client, db)
        sync_partner_sources(client, db)

        log.info("\n👥 Syncing people...")
        sync_application_users(client, db)
        sync_employees(client, db)

        log.info("\n🦷 Syncing clinical data...")
        sync_customers(client, db)
        sync_products(client, db)

        log.info("\n📅 Syncing operations...")
        sync_appointments(client, db)
        sync_dashboard(client, db)

        total_ms = int((time.time() - t0) * 1000)

        # 5. Summary
        cur = db.conn.cursor()
        print(f"\n{'═' * 60}")
        print(f"  SYNC COMPLETE  ({total_ms}ms)")
        print(f"{'═' * 60}")

        tables = [
            'companies', 'application_users', 'customers', 'employees',
            'appointments', 'product_categories', 'products',
            'partner_categories', 'partner_sources', 'dashboard_reports'
        ]
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  {table:30s} → {count:>6} rows")

        return True

    except Exception as e:
        log.error(f"Sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def run_daemon(interval: int = DEFAULT_SYNC_INTERVAL):
    """Run sync continuously"""
    log.info(f"🔄 Starting sync daemon (every {interval}s / {interval//60}min)")
    while True:
        try:
            run_full_sync()
        except Exception as e:
            log.error(f"Sync cycle failed: {e}")

        log.info(f"\n⏳ Next sync in {interval}s...")
        time.sleep(interval)


if __name__ == "__main__":
    if "--daemon" in sys.argv:
        interval = DEFAULT_SYNC_INTERVAL
        if "--interval" in sys.argv:
            idx = sys.argv.index("--interval")
            interval = int(sys.argv[idx + 1])
        run_daemon(interval)
    else:
        run_full_sync()
