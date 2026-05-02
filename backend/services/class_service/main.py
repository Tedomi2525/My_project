from app.routers.classrooms import router as class_router
from app.service_factory import create_service_app


app = create_service_app(
    title="Class Service",
    routers=[class_router],
)
