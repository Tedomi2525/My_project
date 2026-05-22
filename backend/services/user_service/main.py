from app.routers.admins import router as admin_router
from app.routers.account_requests import router as account_request_router
from app.routers.students import router as student_router
from app.routers.teachers import router as teacher_router
from app.service_factory import create_service_app
from app.services.account_request_service import AccountRequestService


app = create_service_app(
    title="User Service",
    routers=[
        admin_router,
        teacher_router,
        student_router,
        account_request_router,
    ],
    create_tables=True,
)

AccountRequestService.ensure_email_columns()
