// src/api.js
export async function fetchHospitalData() {
  try {
    const response = await fetch("http://localhost:5000/api/hospital");
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("Error fetching hospital data:", error);
    return null;
  }
}
