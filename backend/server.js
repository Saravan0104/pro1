// backend/server.js
const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());

app.get("/", (req, res) => {
  res.json({ message: "Hospital IoT LLM Backend is running ✅" });
});

app.get("/api/hospital", (req, res) => {
  res.json({
    waiting_area: { people: 12, co2: "420 ppm", temp: 25 },
    doctor_room: { light: "ON", temp: 22, people: 1 },
    operation_theatre: { temp: 21, humidity: 50, o2: 97, air: "Filtered" },
    patient_room: { temp: 24, presence: "Yes" },
    lab: { power: "ON", equip: "Running" },
    storage: { temp: 20, humidity: 40 }
  });
});

app.listen(5000, () => {
  console.log("✅ Backend running at http://localhost:5000");
});
