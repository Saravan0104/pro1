// src/ControlPanel.jsx
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function ControlPanel() {
  const [devices, setDevices] = useState({
    waitingAreaLight: false,
    doctorRoomAC: false,
    operationTheaterSensor: false,
    patientRoomFan: false,
    testingRoomMachine: false,
  });

  // Base API URL (Render backend)
  const API_URL = "https://pro1-1-back.onrender.com";

  // Fetch current states from backend
  useEffect(() => {
    fetch(`${API_URL}/devices/status`)
      .then((res) => res.json())
      .then((data) => setDevices(data))
      .catch((err) => console.error("Error fetching device status:", err));
  }, []);

  // Toggle device state
  const toggleDevice = async (deviceName) => {
    try {
      const response = await fetch(`${API_URL}/devices/control`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          device: deviceName,
          state: !devices[deviceName],
        }),
      });

      const data = await response.json();
      setDevices((prev) => ({ ...prev, [deviceName]: data.state }));
    } catch (error) {
      console.error("Error updating device:", error);
    }
  };

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
      {Object.keys(devices).map((device) => (
        <div key={device} className="p-4 border rounded-2xl shadow-md bg-white">
          <h2 className="text-lg font-semibold mb-2 capitalize">
            {device.replace(/([A-Z])/g, " $1")}
          </h2>
          <Button
            className={`w-full ${
              devices[device] ? "bg-green-500" : "bg-red-500"
            }`}
            onClick={() => toggleDevice(device)}
          >
            {devices[device] ? "ON" : "OFF"}
          </Button>
        </div>
      ))}
    </div>
  );
}
