from app.routers.exams import router as exam_router
from app.service_factory import create_service_app


app = create_service_app(
    title="Exam Service",
    routers=[exam_router],
)
