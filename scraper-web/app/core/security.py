import hashlib
import secrets

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False


def hash_password(password: str) -> str:
    """Hash password with bcrypt (preferred) or SHA-256 + salt fallback."""
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Fallback to SHA-256 with salt
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored hash. Supports bcrypt, SHA-256+salt, and legacy plain text."""
    if HAS_BCRYPT and stored.startswith("$2"):
        # bcrypt hash
        return bcrypt.checkpw(password.encode(), stored.encode())
    if ':' not in stored:
        # Legacy plain text — accept as-is
        return password == stored
    # SHA-256 with salt
    salt, hashed = stored.split(':', 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
