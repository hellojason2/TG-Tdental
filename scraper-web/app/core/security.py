import secrets
import hashlib

def hash_password(password: str) -> str:
    """Hash password with SHA-256 + salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored hash"""
    if ':' not in stored:
        return password == stored  # legacy plain text
    salt, hashed = stored.split(':', 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
