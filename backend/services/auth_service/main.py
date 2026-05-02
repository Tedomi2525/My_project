from app.routers.auth import router as auth_router
from app.service_factory import create_service_app


app = create_service_app(
    title="Auth Service",
    routers=[auth_router],
    create_tables=True,
)
