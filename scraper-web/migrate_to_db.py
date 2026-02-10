"""
TDental → PostgreSQL Migration Script
Reads scraped API data from full_report.json and imports into Railway database.
"""
import json
import os
import sys

try:
    import psycopg2
    from psycopg2.extras import execute_values, Json
except ImportError:
    print("Installing psycopg2-binary...")
    os.system(f"{sys.executable} -m pip install psycopg2-binary")
    import psycopg2
    from psycopg2.extras import execute_values, Json

DB_URL = "postgresql://postgres:PuQAsTSyIMQOGjOYzjpqnkWbDHeHJjYr@shortline.proxy.rlwy.net:16355/railway"
DATA_DIR = "./data/tamdentist_tdental_vn_20260208_024318"


def connect():
    print(f"  Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    print(f"  ✅ Connected!")
    return conn


def drop_all_tables(conn):
    """Drop all existing tables in the database"""
    cur = conn.cursor()
    cur.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public';
    """)
    tables = [row[0] for row in cur.fetchall()]
    if tables:
        print(f"  Dropping {len(tables)} existing tables: {tables}")
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        cur.execute("GRANT ALL ON SCHEMA public TO public;")
        conn.commit()
        print(f"  ✅ All tables dropped!")
    else:
        print(f"  Database is already empty.")


def create_schema(conn):
    """Create tables based on scraped API data structures"""
    cur = conn.cursor()

    ddl = """
    -- ══════════════════════════════════════════════════════════════
    -- TDental Database Schema (generated from scraped API data)
    -- ══════════════════════════════════════════════════════════════

    -- Scrape metadata
    CREATE TABLE _scrape_metadata (
        id SERIAL PRIMARY KEY,
        target_url TEXT NOT NULL,
        scraped_at TIMESTAMP NOT NULL,
        total_routes INTEGER,
        total_api_calls INTEGER,
        unique_endpoints INTEGER,
        routes JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Companies / Locations
    CREATE TABLE companies (
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
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Application Users
    CREATE TABLE application_users (
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
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Customers / Partners
    CREATE TABLE customers (
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
        city_name_v2 VARCHAR(255),
        ward_name_v2 VARCHAR(255),
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
        company_id UUID REFERENCES companies(id),
        company_name VARCHAR(255),
        appointment_date TIMESTAMP,
        next_appointment_date TIMESTAMP,
        sale_order_date TIMESTAMP,
        last_treatment_complete_date TIMESTAMP,
        job_title VARCHAR(255),
        address TEXT,
        address_v2 TEXT,
        used_address_v2 BOOLEAN DEFAULT FALSE,
        active BOOLEAN DEFAULT TRUE,
        user_id UUID,
        sale_name VARCHAR(255),
        sale_partner_id UUID,
        comment TEXT,
        categories JSONB,
        country_id UUID,
        country VARCHAR(100),
        marketing_staff_id UUID,
        marketing_staff VARCHAR(255),
        contact_status_id UUID,
        contact_status VARCHAR(100),
        potential_level VARCHAR(100),
        service_interests TEXT,
        unactive_by VARCHAR(255),
        unactive_date TIMESTAMP,
        unactive_reason TEXT,
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Product Categories
    CREATE TABLE product_categories (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        complete_name VARCHAR(500),
        parent_id UUID,
        parent JSONB,
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Products
    CREATE TABLE products (
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
        uom_id UUID,
        uom JSONB,
        quantity DECIMAL(15,2) DEFAULT 0,
        is_labo BOOLEAN DEFAULT FALSE,
        display_name VARCHAR(500),
        step_configs JSONB,
        tax_id UUID,
        tax JSONB,
        company_name VARCHAR(255),
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Partner Categories (tags)
    CREATE TABLE partner_categories (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        complete_name VARCHAR(500),
        color VARCHAR(50),
        type VARCHAR(50),
        is_collaborators BOOLEAN DEFAULT FALSE,
        is_active BOOLEAN DEFAULT TRUE,
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Partner Sources (lead sources)
    CREATE TABLE partner_sources (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Card Types
    CREATE TABLE card_types (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- CRM Task Categories
    CREATE TABLE crm_task_categories (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        raw_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- API Endpoints captured
    CREATE TABLE _api_endpoints (
        id SERIAL PRIMARY KEY,
        method VARCHAR(10) NOT NULL,
        path TEXT NOT NULL,
        url TEXT NOT NULL,
        status_codes JSONB,
        call_count INTEGER DEFAULT 0,
        request_sample JSONB,
        response_sample JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Routes discovered
    CREATE TABLE _routes (
        id SERIAL PRIMARY KEY,
        route TEXT NOT NULL UNIQUE,
        page_structure JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Page structures with table/form info
    CREATE TABLE _page_structures (
        id SERIAL PRIMARY KEY,
        route TEXT NOT NULL,
        title TEXT,
        headings JSONB,
        tables JSONB,
        buttons JSONB,
        tabs JSONB,
        forms JSONB,
        inputs JSONB,
        modals JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Indexes
    CREATE INDEX idx_customers_phone ON customers(phone);
    CREATE INDEX idx_customers_email ON customers(email);
    CREATE INDEX idx_customers_company_id ON customers(company_id);
    CREATE INDEX idx_customers_ref ON customers(ref);
    CREATE INDEX idx_customers_treatment_status ON customers(treatment_status);
    CREATE INDEX idx_customers_customer_status ON customers(customer_status);
    CREATE INDEX idx_customers_name ON customers(name);
    CREATE INDEX idx_application_users_username ON application_users(username);
    CREATE INDEX idx_application_users_partner_id ON application_users(partner_id);
    CREATE INDEX idx_products_default_code ON products(default_code);
    CREATE INDEX idx_products_categ_id ON products(categ_id);
    CREATE INDEX idx_product_categories_parent_id ON product_categories(parent_id);
    CREATE INDEX idx_companies_name ON companies(name);
    """

    cur.execute(ddl)
    conn.commit()
    print("  ✅ Schema created with 12 tables + indexes!")


def safe_uuid(val):
    """Convert value to UUID-safe string or None"""
    if val is None or val == '' or val == 'null':
        return None
    return str(val)


def safe_decimal(val):
    """Convert value to decimal or None"""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_timestamp(val):
    """Sanitize timestamp values — TDental uses formats like '--/--/2006' which crash PostgreSQL"""
    if val is None or val == '' or val == 'null':
        return None
    s = str(val)
    # Reject values with dashes used as placeholders (e.g. '--/--/2006', '6/2/----')
    if '--' in s or s.count('-') > 3:
        return None
    # Reject if it's just a year
    if len(s) <= 4 and s.isdigit():
        return None
    return val


def import_data(conn, report):
    """Import scraped data into database tables"""
    cur = conn.cursor()
    endpoints = report['api_endpoints']

    # 1. Insert scrape metadata
    meta = report['metadata']
    cur.execute("""
        INSERT INTO _scrape_metadata (target_url, scraped_at, total_routes, total_api_calls, unique_endpoints, routes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        meta['target_url'], meta['scraped_at'],
        meta['total_routes'], meta['total_api_calls'], meta['unique_endpoints'],
        Json(report['routes'])
    ))
    print(f"  ✅ Metadata inserted")

    # 2. Insert API endpoints
    for key, ep in endpoints.items():
        cur.execute("""
            INSERT INTO _api_endpoints (method, path, url, status_codes, call_count, request_sample, response_sample)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            ep['method'], ep['path'], ep['url'],
            Json(ep.get('status_codes', [])),
            ep.get('call_count', 0),
            Json(ep['request_bodies'][0]) if ep.get('request_bodies') else None,
            Json(ep['response_samples'][0]) if ep.get('response_samples') else None,
        ))
    print(f"  ✅ {len(endpoints)} API endpoints inserted")

    # 3. Insert routes + page structures
    for route in report.get('routes', []):
        cur.execute("INSERT INTO _routes (route) VALUES (%s) ON CONFLICT (route) DO NOTHING", (route,))

    for route, structure in report.get('page_structures', {}).items():
        cur.execute("""
            INSERT INTO _page_structures (route, title, headings, tables, buttons, tabs, forms, inputs, modals)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            route, structure.get('title'),
            Json(structure.get('headings', [])),
            Json(structure.get('tables', [])),
            Json(structure.get('buttons', [])),
            Json(structure.get('tabs', [])),
            Json(structure.get('forms', [])),
            Json(structure.get('inputs', [])),
            Json(structure.get('modals', [])),
        ))
    print(f"  ✅ {len(report.get('routes', []))} routes + {len(report.get('page_structures', {}))} page structures inserted")

    # 4. Companies
    ep = endpoints.get('GET /api/Companies', {})
    for sample in ep.get('response_samples', []):
        items = sample.get('items', sample.get('data', []))
        if not isinstance(items, list):
            items = [sample] if isinstance(sample, dict) and 'id' in sample else []
        for item in items:
            if not isinstance(item, dict) or 'id' not in item:
                continue
            cur.execute("""
                INSERT INTO companies (id, name, logo, active, is_head, period_lock_date,
                    medical_facility_code, hotline, phone, address, address_v2, used_address_v2,
                    tax_code, tax_unit_name, tax_unit_address, tax_bank_name, tax_bank_account,
                    tax_phone, household_businesses, raw_data)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (
                safe_uuid(item['id']), item.get('name'),
                item.get('logo'), item.get('active', True), item.get('isHead', False),
                item.get('periodLockDate'), item.get('medicalFacilityCode'),
                item.get('hotline'), item.get('phone'),
                item.get('address'), item.get('addressV2'), item.get('usedAddressV2', False),
                item.get('taxCode'), item.get('taxUnitName'), item.get('taxUnitAddress'),
                item.get('taxBankName'), item.get('taxBankAccount'), item.get('taxPhone'),
                Json(item.get('householdBusinesses')) if item.get('householdBusinesses') else None,
                Json(item),
            ))
    print(f"  ✅ Companies imported")

    # 5. Application Users
    for ep_key in ['GET /api/ApplicationUsers']:
        ep = endpoints.get(ep_key, {})
        inserted = set()
        for sample in ep.get('response_samples', []):
            items = sample.get('items', sample.get('data', []))
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict) or 'id' not in item:
                    continue
                uid = safe_uuid(item['id'])
                if uid in inserted:
                    continue
                inserted.add(uid)
                cur.execute("""
                    INSERT INTO application_users (id, name, username, partner_id, active,
                        phone_number, job_id, job_name, ref, avatar, employees, team_members, raw_data)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    uid, item.get('name'), item.get('userName'),
                    safe_uuid(item.get('partnerId')), item.get('active', True),
                    item.get('phoneNumber'), safe_uuid(item.get('jobId')),
                    item.get('jobName'), item.get('ref'), item.get('avatar'),
                    Json(item.get('employees')) if item.get('employees') else None,
                    Json(item.get('teamMembers')) if item.get('teamMembers') else None,
                    Json(item),
                ))
        print(f"  ✅ {len(inserted)} Application Users imported")

    # 6. Customers
    ep = endpoints.get('GET /api/Partners/GetPagedPartnersCustomer', {})
    inserted = set()
    for sample in ep.get('response_samples', []):
        items = sample.get('items', sample.get('data', []))
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict) or 'id' not in item:
                continue
            cid = safe_uuid(item['id'])
            if cid in inserted:
                continue
            inserted.add(cid)
            cur.execute("""
                INSERT INTO customers (id, ref, avatar, display_name, name, phone, email, street,
                    city_name, district_name, ward_name, city_name_v2, ward_name_v2,
                    birth_year, birth_month, birthday, date_of_birth, age, gender, gender_display,
                    order_state, order_residual, total_debit, amount_treatment_total, amount_revenue_total,
                    amount_balance, treatment_status, customer_status, customer_type, member_level,
                    card_type, source_id, source_name, company_id, company_name,
                    appointment_date, next_appointment_date, sale_order_date, last_treatment_complete_date,
                    job_title, address, address_v2, used_address_v2, active,
                    user_id, sale_name, sale_partner_id, comment, categories,
                    country_id, country, marketing_staff_id, marketing_staff,
                    contact_status_id, contact_status, potential_level, service_interests,
                    unactive_by, unactive_date, unactive_reason, raw_data)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (
                cid, item.get('ref'), item.get('avatar'),
                item.get('displayName'), item.get('name'), item.get('phone'),
                item.get('email'), item.get('street'),
                item.get('cityName'), item.get('districtName'), item.get('wardName'),
                item.get('cityNameV2'), item.get('wardNameV2'),
                item.get('birthYear'), item.get('birthMonth'), item.get('birthday'),
                safe_timestamp(item.get('dateOfBirth')), item.get('age'),
                item.get('gender'), item.get('genderDisplay'),
                item.get('orderState'), safe_decimal(item.get('orderResidual')),
                safe_decimal(item.get('totalDebit')),
                safe_decimal(item.get('amountTreatmentTotal')),
                safe_decimal(item.get('amountRevenueTotal')),
                safe_decimal(item.get('amountBalance')),
                item.get('treatmentStatus'), item.get('customerStatus'),
                item.get('customerType'), item.get('memberLevel'),
                item.get('cardType'), safe_uuid(item.get('sourceId')),
                item.get('sourceName'), safe_uuid(item.get('companyId')),
                item.get('companyName'),
                safe_timestamp(item.get('appointmentDate')),
                safe_timestamp(item.get('nextAppointmentDate')),
                safe_timestamp(item.get('saleOrderDate')),
                safe_timestamp(item.get('lastTreatmentCompleteDate')),
                item.get('jobTitle'), item.get('address'), item.get('addressV2'),
                item.get('usedAddressV2', False), item.get('active', True),
                safe_uuid(item.get('userId')), item.get('saleName'),
                safe_uuid(item.get('salePartnerId')), item.get('comment'),
                Json(item.get('categories')) if item.get('categories') else None,
                safe_uuid(item.get('countryId')), item.get('country'),
                safe_uuid(item.get('marketingStaffId')), item.get('marketingStaff'),
                safe_uuid(item.get('contactStatusId')), item.get('contactStatus'),
                item.get('potentialLevel'), item.get('serviceInterests'),
                item.get('unactiveBy'), safe_timestamp(item.get('unactiveDate')), item.get('unactiveReason'),
                Json(item),
            ))
    print(f"  ✅ {len(inserted)} Customers imported")

    # 7. Product Categories
    ep = endpoints.get('GET /api/productcategories', {})
    inserted = set()
    for sample in ep.get('response_samples', []):
        items = sample if isinstance(sample, list) else sample.get('items', sample.get('data', []))
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict) or 'id' not in item:
                continue
            pid = safe_uuid(item['id'])
            if pid in inserted:
                continue
            inserted.add(pid)
            cur.execute("""
                INSERT INTO product_categories (id, name, complete_name, parent_id, parent, raw_data)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (
                pid, item.get('name'), item.get('completeName'),
                safe_uuid(item.get('parentId')),
                Json(item.get('parent')) if item.get('parent') else None,
                Json(item),
            ))
    print(f"  ✅ {len(inserted)} Product Categories imported")

    # 8. Products (from autocomplete2)
    ep = endpoints.get('POST /api/products/autocomplete2', {})
    inserted = set()
    for sample in ep.get('response_samples', []):
        items = sample if isinstance(sample, list) else sample.get('items', sample.get('data', []))
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict) or 'id' not in item:
                continue
            pid = safe_uuid(item['id'])
            if pid in inserted:
                continue
            inserted.add(pid)
            cur.execute("""
                INSERT INTO products (id, name, name_no_sign, default_code, price_unit,
                    purchase_price, standard_price, list_price, categ_id, categ,
                    type, type2, firm, labo_price, uom_id, uom,
                    quantity, is_labo, display_name, step_configs,
                    tax_id, tax, company_name, raw_data)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (
                pid, item.get('name'), item.get('nameNoSign'),
                item.get('defaultCode'), safe_decimal(item.get('priceUnit')),
                safe_decimal(item.get('purchasePrice')), safe_decimal(item.get('standardPrice')),
                safe_decimal(item.get('listPrice')),
                safe_uuid(item.get('categId')),
                Json(item.get('categ')) if item.get('categ') else None,
                item.get('type'), item.get('type2'), item.get('firm'),
                safe_decimal(item.get('laboPrice')),
                safe_uuid(item.get('uomId')),
                Json(item.get('uom')) if item.get('uom') else None,
                safe_decimal(item.get('quantity', 0)), item.get('isLabo', False),
                item.get('displayName'),
                Json(item.get('stepConfigs')) if item.get('stepConfigs') else None,
                safe_uuid(item.get('taxId')),
                Json(item.get('tax')) if item.get('tax') else None,
                item.get('companyName'),
                Json(item),
            ))
    print(f"  ✅ {len(inserted)} Products imported")

    # 9. Partner Categories
    ep = endpoints.get('POST /api/Partnercategories/Autocomplete', {})
    inserted = set()
    for sample in ep.get('response_samples', []):
        items = sample if isinstance(sample, list) else sample.get('items', sample.get('data', []))
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict) or 'id' not in item:
                continue
            pid = safe_uuid(item['id'])
            if pid in inserted:
                continue
            inserted.add(pid)
            cur.execute("""
                INSERT INTO partner_categories (id, name, complete_name, color, type, is_collaborators, is_active, raw_data)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (
                pid, item.get('name'), item.get('completeName'),
                str(item.get('color', '')), item.get('type'),
                item.get('isCollaborators', False), item.get('isActive', True),
                Json(item),
            ))
    print(f"  ✅ {len(inserted)} Partner Categories imported")

    # 10. Partner Sources
    ep = endpoints.get('POST /api/PartnerSources/Autocomplete', {})
    inserted = set()
    for sample in ep.get('response_samples', []):
        items = sample if isinstance(sample, list) else sample.get('items', sample.get('data', []))
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict) or 'id' not in item:
                continue
            pid = safe_uuid(item['id'])
            if pid in inserted:
                continue
            inserted.add(pid)
            cur.execute("""
                INSERT INTO partner_sources (id, name, raw_data)
                VALUES (%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (pid, item.get('name'), Json(item)))
    print(f"  ✅ {len(inserted)} Partner Sources imported")

    conn.commit()


def main():
    print("\n" + "=" * 60)
    print("  TDental → Railway PostgreSQL Migration")
    print("=" * 60)

    # Load scraped data
    report_path = os.path.join(DATA_DIR, "full_report.json")
    print(f"\n[1/4] Loading scraped data from {report_path}...")
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    print(f"  ✅ Loaded: {report['metadata']['unique_endpoints']} endpoints, {report['metadata']['total_routes']} routes")

    # Connect
    print(f"\n[2/4] Connecting to database...")
    conn = connect()

    # Drop existing tables
    print(f"\n[3/4] Clearing database...")
    drop_all_tables(conn)

    # Create schema + import
    print(f"\n[4/4] Creating schema and importing data...")
    create_schema(conn)
    import_data(conn, report)

    # Summary
    cur = conn.cursor()
    print(f"\n{'=' * 60}")
    print(f"  MIGRATION COMPLETE!")
    print(f"{'=' * 60}")

    tables = [
        'companies', 'application_users', 'customers', 'product_categories',
        'products', 'partner_categories', 'partner_sources',
        '_api_endpoints', '_routes', '_page_structures', '_scrape_metadata'
    ]
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {table:30s} → {count:>5} rows")

    conn.close()
    print(f"\n  ✅ Done! Database is ready.")


if __name__ == "__main__":
    main()
