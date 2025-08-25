import React, { useState } from "react";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "💬 Chatbot Assistant\nHello 👋 I’m your hospital assistant. How can I help?",
    },
  ]);
  const [input, setInput] = useState("");

  // Device states
  const [deviceStates, setDeviceStates] = useState({
    Fan: "OFF",
    Light: "OFF",
  });

  // Helper to add messages
  const addMessage = (sender, text) => {
    setMessages((prev) => [...prev, { sender, text }]);
  };

  // ---- TIME PARSER (fixed) ----
function parseTime(input) {
  // Match formats like "6:10 pm" or "6.10 pm" or "6 pm"
  const timeRegex = /(\d{1,2})([:.]?(\d{1,2}))?\s*(AM|PM)?/i;
  const match = input.match(timeRegex);

  if (!match) return null;

  let hours = parseInt(match[1], 10);
  let minutes = match[3] ? parseInt(match[3], 10) : 0;
  const ampm = match[4] ? match[4].toUpperCase() : null;

  if (ampm === "PM" && hours < 12) hours += 12;
  if (ampm === "AM" && hours === 12) hours = 0;

  const now = new Date();
  const target = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
    hours,
    minutes,
    0
  );

  // If time already passed today, schedule for tomorrow
  if (target < now) target.setDate(target.getDate() + 1);

  return target;
}
  // ---- SCHEDULER ----
  function scheduleAction(device, action, timeString) {
    const targetTime = parseTime(timeString);
    if (!targetTime) {
      return `⚠️ Could not understand time: "${timeString}"`;
    }

    const delay = targetTime.getTime() - Date.now();

    setTimeout(() => {
      setDeviceStates((prev) => {
        const updated = { ...prev, [device]: action === "on" ? "ON" : "OFF" };
        addMessage("bot", `✅ ${device} turned ${updated[device]} (scheduled)`);
        return updated;
      });
    }, delay);

    return `✅ Okay, I will turn ${action.toUpperCase()} ${device} at ${targetTime.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })}`;
  }

  // ---- HANDLE USER INPUT ----
  const handleSend = () => {
    if (!input.trim()) return;

    const userInput = input.toLowerCase();
    addMessage("user", input);

    let botReply = "I didn't understand that.";
    let action = null;
    let device = null;

    if (userInput.includes("on")) action = "on";
    else if (userInput.includes("off")) action = "off";

    if (userInput.includes("fan")) device = "Fan";
    else if (userInput.includes("light")) device = "Light";

    if (action && device) {
      if (userInput.includes("at")) {
        const timePart = userInput.split("at")[1].trim();
        botReply = scheduleAction(device, action, timePart);
      } else {
        setDeviceStates((prev) => {
          const updated = { ...prev, [device]: action === "on" ? "ON" : "OFF" };
          botReply = `💡 ${device} turned ${updated[device]}`;
          return updated;
        });
      }
    }

    addMessage("bot", botReply);
    setInput("");
  };

  return (
    <div className="border rounded-lg p-4 w-full max-w-md bg-white shadow">
      <h2 className="font-bold mb-2">💬 Chatbot Assistant</h2>
      <div className="h-64 overflow-y-auto border p-2 mb-2 bg-gray-50 rounded">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`mb-1 ${
              msg.sender === "user"
                ? "text-blue-600 text-right"
                : "text-green-700 text-left"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 border p-2 rounded-l"
          placeholder="Type your message..."
        />
        <button
          onClick={handleSend}
          className="bg-blue-500 text-white px-4 rounded-r"
        >
          Send
        </button>
      </div>
    </div>
  );
}
