from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.exam_result import ExamResultResponse
from app.schemas.exam_result_detail import ExamResultDetailBase
from app.services.exam_result_service import ResultService

router = APIRouter(prefix="/results", tags=["Results"])

# 1. Nộp bài thi
@router.post("/submit/{exam_id}/{student_id}", response_model=ExamResultResponse)
def submit_exam(
    exam_id: int,
    student_id: int,
    answers: List[ExamResultDetailBase],
    db: Session = Depends(get_db)
):
    return ResultService.submit_exam(db, exam_id, student_id, answers)

# 2. Xem chi tiết 1 kết quả
@router.get("/{result_id}", response_model=ExamResultResponse)
def get_result(result_id: int, db: Session = Depends(get_db)):
    result = ResultService.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result

# 3. Xem lịch sử thi của học sinh
@router.get("/student/{student_id}", response_model=List[ExamResultResponse])
def get_student_history(student_id: int, db: Session = Depends(get_db)):
    return ResultService.get_student_history(db, student_id)

# 4. Sửa điểm (ví dụ chấm lại)
@router.put("/{result_id}/score")
def update_score(result_id: int, score: float, db: Session = Depends(get_db)):
    result = ResultService.update_result_score(db, result_id, score)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Score updated", "new_score": result.total_score}

# 5. Xóa kết quả
@router.delete("/{result_id}")
def delete_result(result_id: int, db: Session = Depends(get_db)):
    success = ResultService.delete_result(db, result_id)
    if not success:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result deleted"}