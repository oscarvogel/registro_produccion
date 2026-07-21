from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

ALGORITHM = "HS256"
PASSWORD_MAX_BYTES = 72
PASSWORD_TOO_LONG_MESSAGE = "La contrasena es demasiado larga. Usa hasta 72 caracteres o una clave mas corta."
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)


def validate_password_length(password: str) -> None:
    if len(password.encode("utf-8")) > PASSWORD_MAX_BYTES:
        raise ValueError(PASSWORD_TOO_LONG_MESSAGE)


def get_password_hash(password: str) -> str:
    validate_password_length(password)
    return pwd_context.hash(password)


def verify_password(plain_password: str, stored_password: str | None) -> bool:
    if not stored_password:
        return False

    # Backward compatibility for legacy plain-text passwords.
    if stored_password.startswith("$2"):
        return pwd_context.verify(plain_password, stored_password)

    return plain_password == stored_password


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
