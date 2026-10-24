from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.seed_data.demo_company import seed_demo_data

router = APIRouter(prefix="/seed", tags=["Seed & Demo"])

@router.post("/reset-demo")
def reset_and_seed_demo(db: Session = Depends(get_db)):
    """
    Resets or seeds the demonstration environment for NovusBio Health.
    """
    res = seed_demo_data(db)
    return res
