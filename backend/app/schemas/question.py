from pydantic import BaseModel, Field, root_validator
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    content: str
    image_url: Optional[str] = None

class QuestionCreate(QuestionBase):
    # Frontend gửi mảng ["A", "B", "C", "D"]
    options: List[str] = Field(..., min_items=2, max_items=4)
    # Frontend gửi index (0, 1, 2...), Router sẽ đổi sang 'A', 'B'...
    correct_answer: int = Field(..., ge=0, le=3)

class QuestionResponse(QuestionBase):
    question_id: int
    options: List[str] # Trả về mảng cho Vue render
    correct_answer: int # Trả về index
    created_at: datetime

    class Config:
        from_attributes = True

    # Magic: Tự động gom các cột option_a, b... từ DB thành mảng options
    @root_validator(pre=True)
    def map_columns_to_list(cls, values):
        # Kiểm tra nếu values là object SQLAlchemy (ORM mode)
        if not isinstance(values, dict):
            # Map options
            opts = [values.option_a, values.option_b]
            if values.option_c: opts.append(values.option_c)
            if values.option_d: opts.append(values.option_d)
            
            # Map correct_answer từ 'A'/'B' sang 0/1
            map_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
            correct_idx = map_idx.get(values.correct_answer, 0)
            
            # Trả về dict đã xử lý
            return {
                **values.__dict__,
                "options": opts,
                "correct_answer": correct_idx
            }
        return values