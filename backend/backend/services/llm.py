from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# --- In-memory conversation history ---
conversation = []

class ChatRequest(BaseModel):
    query: str

def generate_reply(query: str) -> str:
    q = query.lower()
    ts = datetime.utcnow()

    # --- Example rule-based replies (extendable) ---
    if "temperature" in q:
        return f"Right now, the room temperature is 36°C (updated {ts})."
    elif "heart rate" in q:
        return f"The patient’s heart rate is stable at 78 bpm (checked {ts})."
    elif "oxygen" in q:
        return f"Oxygen saturation is 95% as of {ts}."
    elif "hello" in q or "hi" in q:
        return "Hello 👋 I’m your hospital assistant. How can I help today?"
    else:
        return f"Hmm, I’m not sure about '{query}'. Try asking about temperature, heart rate, oxygen, or humidity."

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    global conversation

    # Add user message
    conversation.append({"role": "user", "content": request.query})

    # Generate reply
    reply = generate_reply(request.query)
    conversation.append({"role": "bot", "content": reply})

    return {"conversation": conversation}
