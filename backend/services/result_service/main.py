from app.routers.results import router as result_router
from app.service_factory import create_service_app


app = create_service_app(
    title="Result Service",
    routers=[result_router],
)
