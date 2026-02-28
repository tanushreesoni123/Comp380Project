import hashlib
from datetime import datetime

def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def money(x: float) -> str:
    return f"${x:,.2f}"