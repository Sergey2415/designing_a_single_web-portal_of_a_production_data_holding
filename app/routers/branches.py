from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Branch, User
from app.schemas import BranchResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["branches"])


@router.get("/branches", response_model=List[BranchResponse])
def get_branches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    branches = db.query(Branch).all()
    result = [BranchResponse(id=0, name="Все филиалы")]
    result.extend([BranchResponse(id=b.id, name=b.name) for b in branches])
    return result








