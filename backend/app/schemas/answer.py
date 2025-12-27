from pydantic import BaseModel

# Input: Sinh viên gửi đáp án lên
class AnswerCreate(BaseModel):
    question_id: int
    selected_option: str # 'A', 'B'...

# Response: Trả về để xác nhận đã lưu
class AnswerResponse(BaseModel):
    answer_id: int
    is_correct: bool # Có thể ẩn field này nếu không muốn SV biết ngay
    
    class Config:
        from_attributes = True