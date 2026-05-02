from app.routers.questions import router as question_router
from app.service_factory import create_service_app


app = create_service_app(
    title="Question Service",
    routers=[question_router],
)
