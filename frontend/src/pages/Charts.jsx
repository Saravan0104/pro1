import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const hospitalData = [
  { section: "Waiting Area", devices: 2 },
  { section: "Doctor Place", devices: 2 },
  { section: "Operation Theater", devices: 3 },
  { section: "Patient Room", devices: 3 },
  { section: "Testing Room", devices: 3 },
];

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A020F0"];

export default function Charts() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-center mb-6">
        📊 Hospital IoT Device Statistics
      </h1>

      {/* Bar Chart */}
      <div className="bg-white p-6 shadow-lg rounded-2xl mb-8">
        <h2 className="text-xl font-semibold mb-4 text-center">
          Devices per Section
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={hospitalData}>
            <XAxis dataKey="section" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="devices" fill="#4F46E5" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Pie Chart */}
      <div className="bg-white p-6 shadow-lg rounded-2xl">
        <h2 className="text-xl font-semibold mb-4 text-center">
          Device Distribution
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={hospitalData}
              dataKey="devices"
              nameKey="section"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label
            >
              {hospitalData.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
