from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..services import database as dbm, llm
from ..models.schemas import ReportOut
from datetime import datetime, timedelta

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/summary", response_model=ReportOut)
def summary(minutes: int = 30, db: Session = Depends(dbm.get_db)):
    since = datetime.utcnow() - timedelta(minutes=minutes)
    alerts = db.query(dbm.AlertRecord).filter(dbm.AlertRecord.ts >= since).all()
    summary_text, recos, ts = llm.summarize_alerts(alerts)
    return ReportOut(summary=summary_text, recommendations=recos, ts=ts)
    async def get_report():
        return{"message":"Reports API is working"}