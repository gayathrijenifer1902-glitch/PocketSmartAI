from datetime import datetime, timedelta, timezone
import bcrypt, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .config import settings
from .db import connection

bearer = HTTPBearer(auto_error=False)
def hash_password(password: str) -> str: return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def verify_password(password: str, hashed: str) -> bool: return bcrypt.checkpw(password.encode(), hashed.encode())
def make_token(user_id: int):
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expires}, settings.secret_key, algorithm="HS256")
def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if not credentials: raise HTTPException(401, "Authentication required")
    try: user_id = int(jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])["sub"])
    except Exception: raise HTTPException(401, "Invalid or expired token")
    with connection() as con: user = con.execute("SELECT id,email,name FROM users WHERE id=?", (user_id,)).fetchone()
    if not user: raise HTTPException(401, "User not found")
    return dict(user)
