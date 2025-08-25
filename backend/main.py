# backend/main.py
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Hospital IoT LLM Backend")

# CORS (allow Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simulated IoT device state ---
devices = {
    "fan": False,
    "light": False,
    "ac": False,
    "temperature": 24,  # °C
}

# scheduler for timed tasks
scheduler = BackgroundScheduler()
scheduler.start()
scheduled_tasks: List[Dict[str, Any]] = []


# Models
class ChatRequest(BaseModel):
    message: str


class DeviceCommand(BaseModel):
    device: str  # "fan" | "light" | "ac" | "temperature"
    state: Optional[bool] = None
    delta: Optional[int] = None  # for temperature +/-


@app.get("/")
def root():
    return {"message": "Hospital IoT LLM Backend is running", "devices": devices}


@app.get("/state")
def get_state():
    return {"devices": devices, "scheduled": scheduled_tasks}


@app.post("/device")
def device_control(cmd: DeviceCommand):
    d = cmd.device.lower()
    if d not in devices:
        return {"ok": False, "error": f"Unknown device '{cmd.device}'", "devices": devices}

    if d == "temperature":
        if cmd.delta is None:
            return {"ok": False, "error": "Provide delta to change temperature", "devices": devices}
        devices["temperature"] = max(16, min(30, devices["temperature"] + int(cmd.delta)))
        return {"ok": True, "message": f"Temperature set to {devices['temperature']}°C", "devices": devices}

    if cmd.state is None:
        return {"ok": False, "error": "Provide state=true/false", "devices": devices}
    devices[d] = bool(cmd.state)
    return {"ok": True, "message": f"{d.capitalize()} turned {'ON' if devices[d] else 'OFF'}", "devices": devices}


# --- Ultra-light NLU for intents ---
def parse_intent(text: str) -> Dict[str, Any]:
    t = text.lower().strip()

    # Small talk
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    thanks = ["thanks", "thank you", "thx"]
    if any(g in t for g in greetings):
        return {"smalltalk": "👋 Hello! How can I help you with the devices?"}
    if any(k in t for k in thanks):
        return {"smalltalk": "You're welcome! 😊"}

    # check for "at <time>" for scheduling
    schedule_match = re.search(r"(turn on|turn off)\s+(fan|light|ac)\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", t)
    if schedule_match:
        action, device, hour, minute, meridian = schedule_match.groups()
        hour = int(hour)
        minute = int(minute) if minute else 0

        # convert to 24h
        if meridian:
            if meridian == "pm" and hour != 12:
                hour += 12
            if meridian == "am" and hour == 12:
                hour = 0

        now = datetime.now()
        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run_time < now:  # schedule for tomorrow
            run_time += timedelta(days=1)

        state = True if "on" in action else False

        def task(dev=device, st=state):
            devices[dev] = st
            print(f"⏰ Scheduled: {dev} {'ON' if st else 'OFF'} executed at {datetime.now()}")

        scheduler.add_job(task, "date", run_date=run_time)
        scheduled_tasks.append({
            "device": device,
            "state": state,
            "time": run_time.strftime("%Y-%m-%d %H:%M")
        })
        return {"schedule": f"✅ Okay, I will {action} {device} at {run_time.strftime('%I:%M %p')}"}

    # synonyms
    synonyms_on = ["on", "start", "enable", "turn on", "switch on"]
    synonyms_off = ["off", "stop", "disable", "turn off", "switch off"]
    inc_words = ["increase", "up", "raise", "+"]
    dec_words = ["decrease", "down", "lower", "-"]

    actions: List[Dict[str, Any]] = []

    if "fan" in t:
        if any(w in t for w in synonyms_on):
            actions.append({"device": "fan", "state": True})
        elif any(w in t for w in synonyms_off):
            actions.append({"device": "fan", "state": False})

    if "light" in t:
        if any(w in t for w in synonyms_on):
            actions.append({"device": "light", "state": True})
        elif any(w in t for w in synonyms_off):
            actions.append({"device": "light", "state": False})

    if "ac" in t or "air conditioner" in t or "aircon" in t:
        if any(w in t for w in synonyms_on):
            actions.append({"device": "ac", "state": True})
        elif any(w in t for w in synonyms_off):
            actions.append({"device": "ac", "state": False})

    if "temp" in t or "temperature" in t:
        m = re.search(r"(-?\d+)", t)
        if any(w in t for w in inc_words):
            delta = int(m.group(1)) if m else 1
            actions.append({"device": "temperature", "delta": abs(delta)})
        elif any(w in t for w in dec_words):
            delta = int(m.group(1)) if m else 1
            actions.append({"device": "temperature", "delta": -abs(delta)})
        else:
            m2 = re.search(r"(?:to|at)\s+(\d{1,2})", t)
            if m2:
                target = int(m2.group(1))
                delta = target - devices["temperature"]
                if delta != 0:
                    actions.append({"device": "temperature", "delta": delta})

    return {"actions": actions}


def apply_actions(actions: List[Dict[str, Any]]) -> List[str]:
    replies: List[str] = []
    for a in actions:
        dev = a.get("device")
        if dev not in devices:
            replies.append(f"⚠️ Unknown device '{dev}'.")
            continue

        if dev == "temperature":
            delta = int(a.get("delta", 0))
            if delta == 0:
                replies.append(f"🌡️ Temperature stays at {devices['temperature']}°C.")
            else:
                devices["temperature"] = max(16, min(30, devices["temperature"] + delta))
                replies.append(f"🌡️ Temperature set to {devices['temperature']}°C.")
        else:
            state = bool(a.get("state", False))
            devices[dev] = state
            icon = {"fan": "🌀", "light": "💡", "ac": "❄️"}.get(dev, "🔧")
            replies.append(f"{icon} {dev.capitalize()} turned {'ON' if state else 'OFF'}.")
    return replies


@app.post("/chat")
def chat(request: ChatRequest):
    query = request.query.lower()
    response = "🤖 I can help control fan, light, AC or adjust temperature. You can also schedule: 'Turn on light at 6 PM'."

    if "turn on fan" in query:
        response = "🌀 Fan turned ON."
    elif "turn off fan" in query:
        response = "🌀 Fan turned OFF."
    elif "turn on light" in query:
        response = "💡 Light turned ON."
    elif "turn off light" in query:
        response = "💡 Light turned OFF."
    elif "turn on ac" in query:
        response = "❄️ AC turned ON."
    elif "turn off ac" in query:
        response = "❄️ AC turned OFF."
    
    # ✅ Add temperature setting for AC
    elif "set ac at" in query or "adjust ac at" in query:
        try:
            temp = int(query.split("at")[-1].strip())
            response = f"❄️ AC temperature set to {temp}°C."
        except:
            response = "⚠️ Please specify a valid temperature (e.g., 'set ac at 18')."
    
    elif "increase ac" in query:
        try:
            temp = int(query.split("at")[-1].strip())
            response = f"❄️ AC temperature increased to {temp}°C."
        except:
            response = "⚠️ Please specify a valid temperature (e.g., 'increase ac at 20')."

    return {"conversation": [{"role": "bot", "content": response}]}




origins = ["*"]  # or your frontend URL after deployment

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
