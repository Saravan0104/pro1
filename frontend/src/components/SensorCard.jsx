import React from "react";
import { Thermometer, HeartPulse, Activity, Battery } from "lucide-react";

export default function SensorCard({ name, value, unit, type }) {
  const icons = {
    temperature: <Thermometer className="h-6 w-6 text-red-500" />,
    heart: <HeartPulse className="h-6 w-6 text-pink-500" />,
    activity: <Activity className="h-6 w-6 text-green-500" />,
    battery: <Battery className="h-6 w-6 text-yellow-500" />,
  };

  return (
    <div className="bg-white shadow rounded-2xl p-4 flex items-center space-x-4">
      {icons[type] || <Activity className="h-6 w-6 text-gray-500" />}
      <div>
        <p className="text-sm text-gray-500">{name}</p>
        <p className="text-xl font-bold">{value} {unit}</p>
      </div>
    </div>
  );
}
