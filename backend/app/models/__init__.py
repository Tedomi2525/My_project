from app.database import Base  # <--- Sửa dòng này
from .user import User
from .classroom import Class
from .class_student import ClassStudent
from .question import Question
from .exam import Exam
from .exam_question import ExamQuestion
from .exam_allowed_student import ExamAllowedStudent
from .exam_result import ExamResult
from .exam_result_detail import ExamResultDetail