from bcrypt import hashpw, gensalt, checkpw

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt."""
    hashed = hashpw(password.encode('utf-8'), gensalt())
    return hashed.decode('utf-8') 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash."""
    return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))