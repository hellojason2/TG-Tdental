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
