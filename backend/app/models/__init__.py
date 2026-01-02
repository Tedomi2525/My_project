from .user import User
from .classroom import Classroom
from .classroom_member import ClassroomMember
from .question import Question
from .exam import Exam, ExamQuestion
from .result import ExamAttempt
from .answer import StudentAnswer

# Để main.py có thể import gọn: "from app.models import User, Exam..."
__all__ = [
    "User", "Classroom", "ClassroomMember", "Question", 
    "Exam", "ExamQuestion", "ExamAttempt", "StudentAnswer"
]