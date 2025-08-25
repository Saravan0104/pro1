import React, { useState } from "react";

// Replace localhost with your Render backend URL
const BASE_URL = "https://your-backend-service.onrender.com";


// --- Embedded Chatbot component (no external import!) ---
function Chatbot({ devices, setDevices }) {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Hi! I can control fan, light, AC and temperature. Try: 'turn on fan', 'increase temperature by 2'." },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const applyDevicesFromBackend = (nextDevices) => {
    if (!nextDevices) return;
    setDevices(nextDevices); // sync dashboard state with server
  };

  const handleSend = async () => {
    if (!input.trim() || busy) return;

    const userText = input.trim();
    setMessages((prev) => [...prev, { sender: "user", text: userText }]);
    setInput("");
    setBusy(true);

    try {
      const res = await fetch(`${BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText }),
      });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();

      // update UI from backend state
      applyDevicesFromBackend(data.devices);

      setMessages((prev) => [...prev, { sender: "bot", text: data.reply }]);
    } catch (err) {
      // graceful fallback: tiny local NLU if backend is down
      const lower = userText.toLowerCase();
      let reply = "⚠️ Backend not reachable. (Tip: start it with uvicorn)";
      const next = { ...devices };
      if (lower.includes("turn on fan")) { next.fan = true; reply = "🌀 Fan turned ON (local)."; }
      else if (lower.includes("turn off fan")) { next.fan = false; reply = "🌀 Fan turned OFF (local)."; }
      else if (lower.includes("turn on light")) { next.light = true; reply = "💡 Light turned ON (local)."; }
      else if (lower.includes("turn off light")) { next.light = false; reply = "💡 Light turned OFF (local)."; }
      else if (lower.includes("turn on ac")) { next.ac = true; reply = "❄️ AC turned ON (local)."; }
      else if (lower.includes("turn off ac")) { next.ac = false; reply = "❄️ AC turned OFF (local)."; }
      else if (lower.includes("increase temp")) { next.temperature = Math.min(30, next.temperature + 1); reply = `🌡️ Temperature set to ${next.temperature}°C (local).`; }
      else if (lower.includes("decrease temp")) { next.temperature = Math.max(16, next.temperature - 1); reply = `🌡️ Temperature set to ${next.temperature}°C (local).`; }

      setDevices(next);
      setMessages((prev) => [...prev, { sender: "bot", text: reply }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-col h-[500px] rounded-2xl border bg-white shadow p-4">
      <h2 className="text-xl font-semibold mb-2">💬 Chatbot Assistant</h2>
      <div className="flex-1 overflow-y-auto space-y-2 bg-gray-50 rounded p-3 border">
        {messages.map((m, i) => (
          <div key={i} className={`w-full flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] px-3 py-2 rounded-lg ${m.sender === "user" ? "bg-blue-600 text-white" : "bg-gray-200 text-black"}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 flex">
        <input
          className="flex-1 border rounded-l-lg px-3 py-2 focus:outline-none"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button
          onClick={handleSend}
          disabled={busy}
          className="bg-blue-600 text-white px-4 py-2 rounded-r-lg disabled:opacity-50"
        >
          {busy ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [devices, setDevices] = useState({
    temperature: 24,
    light: false,
    fan: false,
    ac: false,
  });

  // Helpers to call backend for button clicks (keeps server in sync)
  const setBinary = async (device, state) => {
    setDevices((d) => ({ ...d, [device]: state }));
    try {
      await fetch(`${BASE_URL}/device`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device, state }),
      });
    } catch {}
  };

  const bumpTemp = async (delta) => {
    setDevices((d) => ({ ...d, temperature: Math.max(16, Math.min(30, d.temperature + delta)) }));
    try {
      await fetch(`${BASE_URL}/device`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device: "temperature", delta }),
      });
    } catch {}
  };

  return (
    <div className="p-6 min-h-screen bg-gray-100">
      <h1 className="text-2xl font-bold mb-6">🏥 Hospital IoT Dashboard</h1>

      <div className="grid grid-cols-2 gap-6">
        {/* Left: IoT Panels */}
        <div className="space-y-6">
          {/* Temperature */}
          <div className="bg-white rounded-2xl shadow p-4">
            <h2 className="text-lg font-semibold mb-2">🌡️ Temperature</h2>
            <p className="text-2xl font-bold">{devices.temperature} °C</p>
            <div className="flex gap-2 mt-3">
              <button className="bg-blue-500 text-white px-3 py-1 rounded" onClick={() => bumpTemp(+1)}>
                Increase
              </button>
              <button className="bg-red-500 text-white px-3 py-1 rounded" onClick={() => bumpTemp(-1)}>
                Decrease
              </button>
            </div>
          </div>

          {/* Light */}
          <div className="bg-white rounded-2xl shadow p-4">
            <h2 className="text-lg font-semibold mb-2">💡 Light</h2>
            <p>Status: {devices.light ? "ON ✅" : "OFF ❌"}</p>
            <div className="flex gap-2 mt-3">
              <button className="bg-green-600 text-white px-3 py-1 rounded" onClick={() => setBinary("light", true)}>
                Turn ON
              </button>
              <button className="bg-gray-600 text-white px-3 py-1 rounded" onClick={() => setBinary("light", false)}>
                Turn OFF
              </button>
            </div>
          </div>

          {/* Fan */}
          <div className="bg-white rounded-2xl shadow p-4">
            <h2 className="text-lg font-semibold mb-2">🌀 Fan</h2>
            <p>Status: {devices.fan ? "ON ✅" : "OFF ❌"}</p>
            <div className="flex gap-2 mt-3">
              <button className="bg-green-600 text-white px-3 py-1 rounded" onClick={() => setBinary("fan", true)}>
                Turn ON
              </button>
              <button className="bg-gray-600 text-white px-3 py-1 rounded" onClick={() => setBinary("fan", false)}>
                Turn OFF
              </button>
            </div>
          </div>

          {/* AC */}
          <div className="bg-white rounded-2xl shadow p-4">
            <h2 className="text-lg font-semibold mb-2">❄️ AC</h2>
            <p>Status: {devices.ac ? "ON ✅" : "OFF ❌"}</p>
            <div className="flex gap-2 mt-3">
              <button className="bg-green-600 text-white px-3 py-1 rounded" onClick={() => setBinary("ac", true)}>
                Turn ON
              </button>
              <button className="bg-gray-600 text-white px-3 py-1 rounded" onClick={() => setBinary("ac", false)}>
                Turn OFF
              </button>
            </div>
          </div>
        </div>

        {/* Right: Chatbot */}
        <div>
          <Chatbot devices={devices} setDevices={setDevices} />
        </div>
      </div>
    </div>
  );
}
