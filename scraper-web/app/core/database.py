import psycopg2
import psycopg2.extras
from app.core.config import settings

def get_conn():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a connection object.
    """
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e

def get_cursor(conn):
    """
    Returns a RealDictCursor for the given connection.
    """
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def ensure_auth_tables():
    """Create app_users and app_sessions tables, seed default admin."""
    from app.core.security import hash_password # Import here to avoid circular dependency
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            permissions JSONB DEFAULT '{}',
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
    """)
    # Seed default admin if no users exist
    cur.execute("SELECT COUNT(*) FROM app_users")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO app_users (id, name, email, password, role, active)
            VALUES (%s, %s, %s, %s, 'admin', TRUE)
        """, ('admin_001', 'Admin', 'admin@tdental.vn', hash_password('admin123')))
    conn.commit()
    conn.close()

def ensure_settings_table():
    """Create app_settings table for persistent settings storage."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value JSONB NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Insert default settings if not exist
    default_settings = {
        "app_name": "TDental Viewer",
        "company_name": "Tam Dentist",
        "timezone": "Asia/Ho_Chi_Minh",
        "language": "vi",
        "currency": "VND",
        "date_format": "DD/MM/YYYY",
        "pagination_default": "50",
        "theme": "light",
        "notifications_enabled": True,
        "auto_sync": False,
        "sync_interval": "5"
    }
    for key, value in default_settings.items():
        cur.execute("""
            INSERT INTO app_settings (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO NOTHING
        """, (key, psycopg2.extras.Json(value)))
    conn.commit()
    conn.close()

def ensure_sale_orders_table():
    """Create sale_orders table for Labo/Treatments data."""
    conn = get_conn()
    cur = conn.cursor()
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
            company_id UUID,
            company_name VARCHAR(255),
            doctor_name VARCHAR(255),
            sale_man_name VARCHAR(255),
            raw_data JSONB,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Create indexes for better query performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_so_partner ON sale_orders(partner_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_so_date ON sale_orders(date_order)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_so_state ON sale_orders(state)")
    conn.commit()
    conn.close()


def ensure_all_tables():
    """Create ALL tables referenced by routes.py at startup. Safe to run multiple times."""
    conn = get_conn()
    cur = conn.cursor()

    # customer_appointments
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customer_appointments (
            id UUID PRIMARY KEY,
            partner_id UUID,
            partner_display_name VARCHAR(255),
            partner_ref VARCHAR(50),
            partner_phone VARCHAR(50),
            name VARCHAR(255),
            date TIMESTAMP,
            time VARCHAR(20),
            date_end TIMESTAMP,
            state VARCHAR(50),
            appointment_type VARCHAR(50),
            note TEXT,
            reason TEXT,
            color VARCHAR(50),
            doctor_id UUID,
            doctor_name VARCHAR(255),
            company_id UUID,
            company_name VARCHAR(255),
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ca_partner ON customer_appointments(partner_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ca_date ON customer_appointments(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ca_state ON customer_appointments(state)")

    # companies
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            phone VARCHAR(50),
            email VARCHAR(255),
            address TEXT,
            active BOOLEAN DEFAULT TRUE
        )
    """)

    # customers
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            display_name VARCHAR(255),
            ref VARCHAR(50),
            phone VARCHAR(50),
            email VARCHAR(255),
            gender VARCHAR(20),
            gender_display VARCHAR(20),
            date_of_birth VARCHAR(50),
            birth_year INTEGER,
            birth_month INTEGER,
            age VARCHAR(50),
            address TEXT,
            address_v2 TEXT,
            street VARCHAR(255),
            city_name VARCHAR(255),
            district_name VARCHAR(255),
            ward_name VARCHAR(255),
            country VARCHAR(100),
            job_title VARCHAR(255),
            company_id UUID,
            company_name VARCHAR(255),
            active BOOLEAN DEFAULT TRUE,
            treatment_status VARCHAR(100),
            customer_status VARCHAR(100),
            customer_type VARCHAR(100),
            contact_status VARCHAR(100),
            potential_level VARCHAR(100),
            member_level VARCHAR(100),
            card_type VARCHAR(100),
            source_id UUID,
            source_name VARCHAR(255),
            categories TEXT,
            labels TEXT,
            member_card VARCHAR(255),
            debt DECIMAL(15,2) DEFAULT 0,
            total_debit DECIMAL(15,2) DEFAULT 0,
            total_revenue DECIMAL(15,2) DEFAULT 0,
            total_treatment DECIMAL(15,2) DEFAULT 0,
            amount_treatment_total DECIMAL(15,2) DEFAULT 0,
            amount_revenue_total DECIMAL(15,2) DEFAULT 0,
            amount_balance DECIMAL(15,2) DEFAULT 0,
            order_state VARCHAR(50),
            order_residual DECIMAL(15,2) DEFAULT 0,
            expected_revenue DECIMAL(15,2) DEFAULT 0,
            last_appointment VARCHAR(50),
            appointment_date VARCHAR(50),
            next_appointment VARCHAR(50),
            next_appointment_date VARCHAR(50),
            sale_order_date VARCHAR(50),
            last_treatment VARCHAR(255),
            last_treatment_complete_date VARCHAR(50),
            marketing_staff VARCHAR(255),
            sale_name VARCHAR(255),
            comment TEXT,
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cust_company ON customers(company_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cust_phone ON customers(phone)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cust_name ON customers(name)")

    # employees
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            phone VARCHAR(50),
            email VARCHAR(255),
            company_id UUID,
            company_name VARCHAR(255),
            is_doctor BOOLEAN DEFAULT FALSE,
            active BOOLEAN DEFAULT TRUE,
            hr_job VARCHAR(255),
            hr_job_title VARCHAR(255),
            department VARCHAR(255),
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # products
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            display_name VARCHAR(255),
            default_code VARCHAR(100),
            categ_id UUID,
            categ_name VARCHAR(255),
            type VARCHAR(50),
            list_price DECIMAL(15,2),
            standard_price DECIMAL(15,2),
            company_id UUID,
            company_name VARCHAR(255),
            is_labo BOOLEAN DEFAULT FALSE,
            active BOOLEAN DEFAULT TRUE,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # product_categories
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_categories (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            parent_id UUID,
            complete_name TEXT
        )
    """)

    # partner_categories
    cur.execute("""
        CREATE TABLE IF NOT EXISTS partner_categories (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            active BOOLEAN DEFAULT TRUE
        )
    """)

    # partner_sources
    cur.execute("""
        CREATE TABLE IF NOT EXISTS partner_sources (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            active BOOLEAN DEFAULT TRUE
        )
    """)

    # account_payments
    cur.execute("""
        CREATE TABLE IF NOT EXISTS account_payments (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            date TIMESTAMP,
            payment_date TIMESTAMP,
            amount DECIMAL(15,2),
            amount_signed DECIMAL(15,2),
            payment_type VARCHAR(50),
            display_payment_type VARCHAR(100),
            journal_name VARCHAR(255),
            journal_type VARCHAR(50),
            partner_id UUID,
            partner_name VARCHAR(255),
            state VARCHAR(50),
            display_state VARCHAR(100),
            company_id UUID,
            company_name VARCHAR(255),
            communication TEXT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ap_partner ON account_payments(partner_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ap_date ON account_payments(payment_date)")

    # sale_order_lines
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sale_order_lines (
            id UUID PRIMARY KEY,
            order_id UUID,
            partner_id UUID,
            product_id UUID,
            product_name TEXT,
            name TEXT,
            product_uom_qty DECIMAL(15,2),
            price_unit DECIMAL(15,2),
            price_subtotal DECIMAL(15,2),
            amount_total DECIMAL(15,2),
            discount DECIMAL(5,2),
            state VARCHAR(50),
            teeth TEXT,
            diagnostic TEXT,
            doctor_id UUID,
            doctor_name VARCHAR(255)
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sol_order ON sale_order_lines(order_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sol_partner ON sale_order_lines(partner_id)")

    # sale_order_payments
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sale_order_payments (
            id UUID PRIMARY KEY,
            sale_order_id UUID,
            order_id UUID,
            amount DECIMAL(15,2),
            date TIMESTAMP,
            payment_type VARCHAR(50),
            journal_name VARCHAR(255),
            note TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sop_order ON sale_order_payments(order_id)")

    # stock_pickings
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_pickings (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            date TIMESTAMP,
            date_done TIMESTAMP,
            partner_id UUID,
            partner_name VARCHAR(255),
            picking_type VARCHAR(50),
            state VARCHAR(50),
            company_id UUID,
            company_name VARCHAR(255),
            origin VARCHAR(255),
            total_amount DECIMAL(15,2),
            created_by_name VARCHAR(255),
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sp_date ON stock_pickings(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sp_state ON stock_pickings(state)")

    # stock_moves
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_moves (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            reference VARCHAR(255),
            origin VARCHAR(255),
            product_id UUID,
            product_name VARCHAR(255),
            product_default_code VARCHAR(100),
            product_uom_name VARCHAR(50),
            product_uom_qty DECIMAL(15,2),
            product_qty DECIMAL(15,2),
            price_unit DECIMAL(15,2),
            total_amount DECIMAL(15,2),
            amount DECIMAL(15,2),
            date TIMESTAMP,
            date_done TIMESTAMP,
            picking_id UUID,
            state VARCHAR(50),
            is_in BOOLEAN DEFAULT FALSE,
            is_out BOOLEAN DEFAULT FALSE,
            location_id VARCHAR(255),
            location_dest_id VARCHAR(255),
            company_id UUID,
            company_name VARCHAR(255),
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sm_product ON stock_moves(product_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sm_date ON stock_moves(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sm_picking ON stock_moves(picking_id)")

    # dot_khams (exam sessions)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dot_khams (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            partner_id UUID,
            sale_order_id UUID,
            date TIMESTAMP,
            state VARCHAR(50),
            doctor_id UUID,
            doctor_name VARCHAR(255),
            company_id UUID,
            company_name VARCHAR(255),
            reason TEXT,
            note TEXT,
            amount_total DECIMAL(15,2),
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dk_partner ON dot_khams(partner_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dk_date ON dot_khams(date)")

    # quotations
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quotations (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            partner_id UUID,
            date TIMESTAMP,
            state VARCHAR(50),
            amount_total DECIMAL(15,2),
            note TEXT,
            doctor_id UUID,
            doctor_name VARCHAR(255),
            company_id UUID,
            company_name VARCHAR(255),
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_quot_partner ON quotations(partner_id)")

    # customer_receipts
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customer_receipts (
            id UUID PRIMARY KEY,
            partner_id UUID,
            date TIMESTAMP,
            state VARCHAR(50),
            doctor_id UUID,
            doctor_name VARCHAR(255),
            company_id UUID,
            company_name VARCHAR(255),
            reason TEXT,
            note TEXT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cr_partner ON customer_receipts(partner_id)")

    # commissions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS commissions (
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            partner_id UUID,
            amount DECIMAL(15,2),
            date TIMESTAMP,
            state VARCHAR(50),
            type VARCHAR(50),
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # dashboard_reports
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dashboard_reports (
            id SERIAL PRIMARY KEY,
            company_id UUID,
            company_name VARCHAR(255),
            date DATE,
            total_revenue DECIMAL(15,2),
            total_cash DECIMAL(15,2),
            total_bank DECIMAL(15,2),
            total_other DECIMAL(15,2),
            total_debt DECIMAL(15,2),
            total_customers INTEGER,
            new_customers INTEGER,
            total_appointments INTEGER,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
