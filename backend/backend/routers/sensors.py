from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.schemas import BulkSensorPayload, SensorPoint, AlertOut
from ..services import database as dbm, processor

router = APIRouter(prefix="/sensors", tags=["sensors"])

@router.post("/ingest", response_model=dict)
def ingest(payload: BulkSensorPayload, db: Session = Depends(dbm.get_db)):
    processor.persist_points(db, payload.points)
    alerts = processor.evaluate_points(db, payload.points)
    out = [AlertOut(area=a.area, severity=a.severity, message=a.message, ts=a.ts) for a in alerts]
    return {"stored": len(payload.points), "alerts": out}

@router.get("/latest", response_model=list[dict])
def latest(db: Session = Depends(dbm.get_db)):
    q = db.query(dbm.SensorRecord).order_by(dbm.SensorRecord.ts.desc()).limit(100)
    return [
        {"area": r.area, "metric": r.metric, "value": r.value, "unit": r.unit, "ts": r.ts}
        for r in q
    ]
