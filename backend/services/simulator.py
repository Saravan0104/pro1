import random, time, requests
from datetime import datetime, timedelta
from typing import Dict, Any

API = "http://127.0.0.1:8000/sensors/ingest"

AREAS = {
    "waiting_area": [
        ("human_count","count"), ("co2","ppm"), ("temp","°C")
    ],
    "doctor_room": [
        ("light","%"), ("temp","°C"), ("human_count","count")
    ],
    "operation_theatre": [
        ("temp","°C"), ("humidity","%"), ("oxygen","%"), ("air_quality","AQI")
    ],
    "patient_room": [
        ("temp","°C"), ("presence_inactive_minutes","min")
    ],
    "testing_room": [
        ("power_kw","kW"), ("equipment_active","count")
    ],
    "medicine_storage": [
        ("temp","°C"), ("humidity","%")
    ],
}

def sample(area: str, metric: str) -> float:
    rng = {
        "human_count": (0, 40),
        "co2": (400, 1600),
        "temp": (16, 32),
        "light": (0, 100),
        "humidity": (30, 90),
        "oxygen": (18.0, 21.0),
        "air_quality": (10, 180),
        "presence_inactive_minutes": (0, 240),
        "power_kw": (2, 25),
        "equipment_active": (0, 6),
    }
    lo, hi = rng.get(metric, (0, 100))
    val = random.uniform(lo, hi)
    # nudge “problematic” states occasionally
    if area == "operation_theatre" and metric == "humidity" and random.random() < 0.2:
        val = random.uniform(72, 88)
    if area == "medicine_storage" and metric == "temp" and random.random() < 0.2:
        val = random.uniform(8.5, 12.0)
    if area == "waiting_area" and metric == "co2" and random.random() < 0.2:
        val = random.uniform(1200, 1500)
    return round(val, 2)

def make_point(area:str, metric:str, unit:str) -> Dict[str, Any]:
    return {
        "area": area,
        "metric": metric,
        "value": sample(area, metric),
        "unit": unit,
        "ts": datetime.utcnow().isoformat()
    }

def loop(period_sec: float = 2.0):
    print("Simulator started. Posting to", API)
    while True:
        points = []
        for area, metrics in AREAS.items():
            for metric, unit in metrics:
                points.append(make_point(area, metric, unit))
        try:
            r = requests.post(API, json={"points": points}, timeout=5)
            if r.ok:
                payload = r.json()
                alerts = payload.get("alerts", [])
                if alerts:
                    print(f"[{datetime.utcnow().isoformat()}] Alerts:")
                    for a in alerts:
                        print("  -", a["area"], a["severity"], a["message"])
            else:
                print("POST failed:", r.status_code, r.text)
        except Exception as e:
            print("Error posting:", e)
        time.sleep(period_sec)

if __name__ == "__main__":
    loop(2.0)
