import os
from typing import Any

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS


SERVICE_URLS = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8101"),
    "user": os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8102"),
    "class": os.getenv("CLASS_SERVICE_URL", "http://127.0.0.1:8103"),
    "question": os.getenv("QUESTION_SERVICE_URL", "http://127.0.0.1:8104"),
    "exam": os.getenv("EXAM_SERVICE_URL", "http://127.0.0.1:8105"),
    "result": os.getenv("RESULT_SERVICE_URL", "http://127.0.0.1:8106"),
}

ROUTE_PREFIXES = {
    "/login": "auth",
    "/admins": "user",
    "/teachers": "user",
    "/students": "user",
    "/classes": "class",
    "/questions": "question",
    "/exams": "exam",
    "/results": "result",
}

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
}

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def resolve_service(path: str) -> str | None:
    for prefix, service_name in ROUTE_PREFIXES.items():
        if path == prefix or path.startswith(f"{prefix}/"):
            return service_name
    return None


def filtered_headers(headers: dict[str, Any]) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "API Gateway"}


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy(path: str, request: Request):
    request_path = f"/{path}"
    service_name = resolve_service(request_path)
    if not service_name:
        return Response(
            content='{"detail":"Route not found in gateway"}',
            status_code=404,
            media_type="application/json",
        )

    target_url = f"{SERVICE_URLS[service_name]}{request_path}"

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        service_response = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            content=await request.body(),
            headers=filtered_headers(dict(request.headers)),
        )

    return Response(
        content=service_response.content,
        status_code=service_response.status_code,
        headers=filtered_headers(dict(service_response.headers)),
        media_type=service_response.headers.get("content-type"),
    )
