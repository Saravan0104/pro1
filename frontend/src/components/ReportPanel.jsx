// src/ReportPanel.jsx
import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";

export default function ReportPanel() {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/reports")
      .then((res) => res.json())
      .then((data) => setReports(data))
      .catch((err) => console.error("Error fetching reports:", err));
  }, []);

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
      {reports.length === 0 ? (
        <p className="text-gray-500">No reports available yet.</p>
      ) : (
        reports.map((report, idx) => (
          <Card key={idx} className="shadow-md rounded-2xl">
            <CardContent className="p-4">
              <h2 className="text-lg font-semibold mb-2">{report.title}</h2>
              <p className="text-sm text-gray-700">{report.description}</p>
              <p className="text-xs text-gray-400 mt-2">
                Generated on: {report.timestamp}
              </p>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
