from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import json

app = FastAPI()

# CORS to prevent "Backend not reachable"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pro1-1-front.onrender.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation history
conversation = []

# Load pre-trained GPT-2 (no fine-tuning)
model_path = "gpt2"  # Uses pre-trained model, no API key needed
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Simulated IoT control
def control_device(device: str, action: str, value: int = None):
    if action in ["on", "off"]:
        return f"{device.capitalize()} turned {action.upper()}"
    elif action in ["increase", "decrease"]:
        return f"{device.capitalize()} {action}d by {value or 'unknown'}"
    elif action == "check":
        return f"{device.capitalize()} checked"
    return "No valid action"

class ChatRequest(BaseModel):
    query: str

def generate_reply(query: str) -> str:
    try:
        # Prompt for GPT-2
        prompt = f"""
        Analyze: '{query}'
        1. Tokenize: Break into words.
        2. Sentiment: positive/negative/neutral/mixed, reason.
        3. Intent: Extract device (fan/light/AC/temperature/heater/room), action (on/off/increase/decrease/check/maintain), value.
        Output JSON: {{"tokens": [...], "sentiment": "...", "sentiment_reason": "...", "intent": {{"device": "...", "action": "...", "value": null}}, "conversational_response": "..."}}}
        """
        inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
        outputs = model.generate(inputs, max_length=300, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Parse JSON
        try:
            analysis = json.loads(generated.split("Output JSON:")[1].strip() if "Output JSON:" in generated else generated)
        except:
            # Fallback if JSON parsing fails
            analysis = {
                "tokens": query.lower().split(),
                "sentiment": "neutral",
                "sentiment_reason": "Assumed neutral due to parsing failure",
                "intent": {"device": None, "action": None, "value": None},
                "conversational_response": f"Let me try that again: {query}"
            }
        
        # Execute IoT simulation
        intent = analysis.get("intent", {})
        task_status = control_device(intent.get("device"), intent.get("action"), intent.get("value"))
        
        # Use conversational response or fallback
        conversational_response = analysis.get("conversational_response", task_status)
        if intent.get("device") is None:
            conversational_response = f"Sorry, I didn’t understand '{query}'. Try asking about fan, light, AC, or temperature!"
        
        ts = datetime.utcnow()
        return f"{conversational_response} (processed {ts})"
    except Exception as e:
        ts = datetime.utcnow()
        return f"Hmm, I’m not sure about '{query}'. Try asking about fan, light, AC, or temperature (processed {ts})."

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    global conversation
    conversation.append({"role": "user", "content": request.query})
    reply = generate_reply(request.query)
    conversation.append({"role": "bot", "content": reply})
    return {"conversation": conversation}

@app.get("/")
def root():
    return {"message": "FastAPI backend with pre-trained GPT-2 running"}