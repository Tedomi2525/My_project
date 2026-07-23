from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import ALGORITHM, SECRET_KEY
from app.database import SessionLocal
from app.models.audit_log import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    """Records successful authenticated state-changing API calls."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if (
            request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and response.status_code < 400
            and request.url.path not in {"/login", "/forgot-password", "/reset-password"}
        ):
            authorization = request.headers.get("authorization", "")
            if authorization.lower().startswith("bearer "):
                try:
                    payload = jwt.decode(
                        authorization.split(" ", 1)[1],
                        SECRET_KEY,
                        algorithms=[ALGORITHM],
                    )
                    actor_id = int(payload["user_id"])
                    actor_role = str(payload["role"])
                    segments = [part for part in request.url.path.split("/") if part]
                    entity_type = segments[0] if segments else "api"
                    entity_id = next(
                        (part for part in segments[1:] if part.isdigit()), None
                    )
                    db = SessionLocal()
                    try:
                        db.add(AuditLog(
                            actor_role=actor_role,
                            actor_id=actor_id,
                            actor_name=payload.get("full_name"),
                            action=f"{request.method.lower()}_{entity_type}",
                            entity_type=entity_type,
                            entity_id=entity_id,
                            details={
                                "path": request.url.path,
                                "status_code": response.status_code,
                            },
                        ))
                        db.commit()
                    finally:
                        db.close()
                except (JWTError, KeyError, TypeError, ValueError):
                    pass
        return response
