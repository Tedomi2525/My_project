from app.routers.admins import router as admin_router
from app.routers.students import router as student_router
from app.routers.teachers import router as teacher_router
from app.service_factory import create_service_app


app = create_service_app(
    title="User Service",
    routers=[
        admin_router,
        teacher_router,
        student_router,
    ],
)
