from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionResponse
from app.services import QuestionService
from app.dependencies import get_current_teacher

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("/", response_model=QuestionResponse)
def create_question(
    question: QuestionCreate, 
    db: Session = Depends(get_db), 
    teacher: User = Depends(get_current_teacher)
):
    return QuestionService.create_question(db, question, teacher_id=teacher.user_id)

@router.get("/", response_model=List[QuestionResponse])
def get_my_questions(
    db: Session = Depends(get_db), 
    teacher: User = Depends(get_current_teacher)
):
    return QuestionService.get_questions_by_teacher(db, teacher.user_id)
# app/routers/questions.py (Thêm vào cuối file)
from fastapi import HTTPException, status

# API Sửa câu hỏi
@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    try:
        updated_q = QuestionService.update_question(db, question_id, question_data, teacher.user_id)
        if not updated_q:
            raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
        return updated_q
    except Exception as e:
        # Nếu lỗi do không phải chủ sở hữu
        if str(e) == "Permission Denied":
            raise HTTPException(status_code=403, detail="Bạn không có quyền sửa câu hỏi này")
        raise e

# API Xóa câu hỏi
@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    try:
        success = QuestionService.delete_question(db, question_id, teacher.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
        return None # 204 No Content thì không cần return body
    except Exception as e:
        if str(e) == "Permission Denied":
            raise HTTPException(status_code=403, detail="Bạn không có quyền xóa câu hỏi này")
        raise e