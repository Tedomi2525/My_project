from enum import Enum
from typing import Union


class UserRole(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


def normalize_role(role: Union[str, UserRole, None]) -> str:
    if role is None:
        return ""
    if isinstance(role, UserRole):
        return role.value
    return str(role).strip().lower()
