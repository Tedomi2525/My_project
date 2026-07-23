import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class LoginRateLimitMiddleware(BaseHTTPMiddleware):
    """Small in-process IP limiter for the login endpoint."""

    WINDOW_SECONDS = 5 * 60
    MAX_FAILURES = 10
    failures = defaultdict(deque)

    async def dispatch(self, request, call_next):
        if request.url.path != "/login" or request.method != "POST":
            return await call_next(request)

        forwarded = request.headers.get("x-forwarded-for", "")
        client_ip = forwarded.split(",", 1)[0].strip() or (
            request.client.host if request.client else "unknown"
        )
        now = time.monotonic()
        attempts = self.failures[client_ip]
        while attempts and now - attempts[0] > self.WINDOW_SECONDS:
            attempts.popleft()
        if len(attempts) >= self.MAX_FAILURES:
            retry_after = max(1, int(self.WINDOW_SECONDS - (now - attempts[0])))
            return JSONResponse(
                {"detail": "Quá nhiều lần đăng nhập sai. Vui lòng thử lại sau."},
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        if response.status_code == 401:
            attempts.append(now)
        elif response.status_code < 400:
            attempts.clear()
        return response
