import secrets
from fastapi import Header, HTTPException, status
from app.core.config import settings


async def verify_service_token(authorization: str | None = Header(default=None)):
    # Protege la comunicación Java -> Python cuando se configura un token.
    if not settings.service_token:
        return True

    expected = f"Bearer {settings.service_token}"
    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de servicio inválidas.",
        )
    return True
