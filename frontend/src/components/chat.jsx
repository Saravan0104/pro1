// frontend/src/components/Chatbot.jsx
import React, { useState } from "react";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Show user message
    const newMessages = [...messages, { sender: "You", text: input }];
    setMessages(newMessages);

    try {
      const response = await fetch("https://pro1-1-back.onrender.com", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();

      // Show bot reply
      setMessages([...newMessages, { sender: "Bot", text: data.reply }]);
    } catch (err) {
      setMessages([...newMessages, { sender: "Bot", text: "⚠️ No reply from server" }]);
    }

    setInput("");
  };

  return (
    <div className="p-4 bg-white rounded-2xl shadow-lg h-80 flex flex-col">
      <h2 className="text-lg font-bold mb-2">💬 Chatbot Assistant</h2>
      <div className="flex-1 overflow-y-auto border p-2 rounded mb-2 bg-gray-50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-1 ${msg.sender === "You" ? "text-blue-600" : "text-green-600"}`}>
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 border rounded p-2"
          placeholder="Type your message..."
        />
        <button
          onClick={sendMessage}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Send
        </button>
      </div>
    </div>
  );
}
