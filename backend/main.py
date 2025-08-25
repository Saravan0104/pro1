import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import re
import logging

# Configure logging for Render (console and file)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()  # For Render's log viewer
    ]
)

app = FastAPI(title="Hospital IoT LLM Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pro1-1-front.onrender.com",
        "http://localhost:3000"  # For local dev
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Simulated IoT device state
devices = {
    "fan": False,
    "light": False,
    "ac": False,
    "temperature": 24,  # °C
}

# Scheduler for timed tasks
scheduler = BackgroundScheduler()
scheduler.start()
scheduled_tasks: List[Dict[str, Any]] = []

# Models
class ChatRequest(BaseModel):
    message: str

class DeviceCommand(BaseModel):
    device: str
    state: Optional[bool] = None
    delta: Optional[int] = None

@app.get("/")
def root():
    logging.info("Root endpoint accessed")
    return {"message": "Hospital IoT LLM Backend is running on Render", "devices": devices}

@app.get("/state")
def get_state():
    logging.info("State endpoint accessed")
    return {"devices": devices, "scheduled": scheduled_tasks}

@app.post("/device")
def device_control(cmd: DeviceCommand):
    d = cmd.device.lower()
    if d not in devices:
        logging.error(f"Unknown device: {d}")
        raise HTTPException(status_code=400, detail=f"Unknown device '{cmd.device}'")
    
    if d == "temperature":
        if cmd.delta is None:
            logging.error("Temperature change requires delta")
            raise HTTPException(status_code=400, detail="Provide delta to change temperature")
        devices["temperature"] = max(16, min(30, devices["temperature"] + int(cmd.delta)))
        logging.info(f"Temperature set to {devices['temperature']}°C")
        return {"ok": True, "message": f"Temperature set to {devices['temperature']}°C", "devices": devices}

    if cmd.state is None:
        logging.error("Device state change requires state")
        raise HTTPException(status_code=400, detail="Provide state=true/false")
    devices[d] = bool(cmd.state)
    logging.info(f"{d.capitalize()} turned {'ON' if devices[d] else 'OFF'}")
    return {"ok": True, "message": f"{d.capitalize()} turned {'ON' if devices[d] else 'OFF'}", "devices": devices}

# Ultra-light NLU for intents
def parse_intent(text: str) -> Dict[str, Any]:
    t = text.lower().strip()
    logging.info(f"Parsing intent for query: {t}")

    # Small talk
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    thanks = ["thanks", "thank you", "thx"]
    if any(g in t for g in greetings):
        return {"smalltalk": "👋 Hello! How can I help you with the devices?"}
    if any(k in t for k in thanks):
        return {"smalltalk": "You're welcome! 😊"}

    # Check for scheduling
    schedule_match = re.search(r"(turn on|turn off)\s+(fan|light|ac)\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", t)
    if schedule_match:
        action, device, hour, minute, meridian = schedule_match.groups()
        hour = int(hour)
        minute = int(minute) if minute else 0

        # Convert to 24h
        if meridian:
            if meridian == "pm" and hour != 12:
                hour += 12
            if meridian == "am" and hour == 12:
                hour = 0

        now = datetime.now()
        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run_time < now:
            run_time += timedelta(days=1)

        state = True if "on" in action else False

        def task(dev=device, st=state):
            devices[dev] = st
            logging.info(f"Scheduled task: {dev} {'ON' if st else 'OFF'} at {datetime.now()}")

        scheduler.add_job(task, "date", run_date=run_time)
        scheduled_tasks.append({
            "device": device,
            "state": state,
            "time": run_time.strftime("%Y-%m-%d %H:%M")
        })
        logging.info(f"Scheduled {action} {device} at {run_time.strftime('%I:%M %p')}")
        return {"schedule": f"✅ Okay, I will {action} {device} at {run_time.strftime('%I:%M %p')}"}

    # Synonyms for actions
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

    if "temp" in t or "temperature" in t or "ac" in t:
        m = re.search(r"(-?\d+)", t)
        m2 = re.search(r"(?:to|at)\s+(\d{1,2})", t)
        if any(w in t for w in inc_words):
            delta = int(m.group(1)) if m else 1
            actions.append({"device": "temperature", "delta": abs(delta)})
        elif any(w in t for w in dec_words):
            delta = int(m.group(1)) if m else 1
            actions.append({"device": "temperature", "delta": -abs(delta)})
        elif m2:
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
    try:
        query = request.message.lower()
        logging.info(f"Received chat request: {query}")
        intent = parse_intent(query)
        logging.info(f"Intent parsed: {intent}")

        conversation = [{"role": "user", "content": request.message}]

        if "smalltalk" in intent:
            response = intent["smalltalk"]
        elif "schedule" in intent:
            response = intent["schedule"]
        elif "actions" in intent and intent["actions"]:
            responses = apply_actions(intent["actions"])
            response = " ".join(responses)
        else:
            response = "🤖 I can help control fan, light, AC, or adjust temperature. You can also schedule: 'Turn on light at 6 PM'."

        conversation.append({"role": "bot", "content": response})
        logging.info(f"Response sent: {response}")
        return {"conversation": conversation}
    except Exception as e:
        logging.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("Scheduler shut down")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render sets PORT env variable
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)