from pydantic import BaseModel

class StudentAnswerBase(BaseModel):
    answer_id: int
    question_id: int
    selected_option: str
    is_correct: bool

    class Config:
        from_attributes = True

# Schema dùng để nhận dữ liệu nộp bài (chỉ cần ID câu hỏi và index chọn)
class AnswerSubmit(BaseModel):
    question_id: int
    selected_option_index: int # -1 nếu không chọn