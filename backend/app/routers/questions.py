from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("/", response_model=List[schemas.QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    # Schema sẽ tự động gộp option_a,b,c,d thành mảng options nhờ @root_validator
    return db.query(models.Question).all()

@router.post("/", response_model=schemas.QuestionResponse)
def create_question(q: schemas.QuestionCreate, db: Session = Depends(get_db)):
    # Logic Map: Index (0,1,2,3) -> Char ('A','B','C','D')
    index_to_char = ['A', 'B', 'C', 'D']
    correct_char = index_to_char[q.correct_answer]
    
    # Logic Map: Array -> Columns
    db_question = models.Question(
        content=q.content,
        image_url=q.image_url,
        teacher_id=1,  # Hardcode ID teacher (Thực tế lấy từ Token)
        option_a=q.options[0],
        option_b=q.options[1],
        option_c=q.options[2] if len(q.options) > 2 else None,
        option_d=q.options[3] if len(q.options) > 3 else None,
        correct_answer=correct_char
    )
    
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question