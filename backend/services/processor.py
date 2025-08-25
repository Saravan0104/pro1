from typing import Iterable, List, Tuple
from datetime import datetime
from . import database as dbm

# simple hospital thresholds (tweak freely)
THRESHOLDS = {
    ("operation_theatre", "humidity"): ("<", 70, "OT humidity should be < 70%"),
    ("operation_theatre", "oxygen"): (">=", 19.5, "OT oxygen >= 19.5% recommended"),
    ("medicine_storage", "temp"): ("between", (2,8), "Vaccine storage 2–8°C"),
    ("waiting_area", "co2"): ("<", 1000, "CO₂ < 1000 ppm for comfort"),
    ("patient_room", "presence_inactive_minutes"): ("<", 120, "Inactivity < 120 min"),
    ("testing_room", "power_kw"): ("<", 20, "Lab power < 20 kW"),
}

def check_point(area: str, metric: str, value: float) -> Tuple[str,str] | None:
    key = (area, metric)
    if key not in THRESHOLDS:
        return None
    rule, target, note = THRESHOLDS[key]
    ok = True
    if rule == "<":
        ok = value < float(target)
    elif rule == ">=":
        ok = value >= float(target)
    elif rule == "between":
        low, high = target
        ok = (low <= value <= high)
    if ok:
        return ("INFO", f"{metric} OK — {note}")
    else:
        sev = "ALERT" if area in ["operation_theatre","medicine_storage"] else "WARN"
        return (sev, f"{metric} out of range ({value}). Expected {note}")

def persist_points(db, points: Iterable):
    for p in points:
        rec = dbm.SensorRecord(area=p.area, metric=p.metric, value=p.value, unit=p.unit, ts=p.ts)
        db.add(rec)
    db.commit()

def evaluate_points(db, points: Iterable) -> List[dbm.AlertRecord]:
    alerts = []
    for p in points:
        res = check_point(p.area, p.metric, p.value)
        if res:
            severity, message = res
            alert = dbm.AlertRecord(area=p.area, severity=severity, message=message, ts=p.ts)
            db.add(alert)
            alerts.append(alert)
    db.commit()
    return alerts
