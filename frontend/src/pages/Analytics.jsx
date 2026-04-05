import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";

import ChartCard from "../components/ChartCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { analyticsService } from "../services";

const pieColors = ["#0b4f6c", "#1f8ea3", "#94a3b8"];

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    analyticsService.summary().then(setData);
  }, []);

  if (!data) return <LoadingSpinner label="Loading analytics" />;

  const bloodTypeData = Object.entries(data.blood_type_demand).map(([type, count]) => ({ type, count }));
  const availabilityData = Object.entries(data.availability_stats).map(([status, value]) => ({ status, value }));

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <ChartCard title="Blood Type Request Distribution">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={bloodTypeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="type" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#0b4f6c" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Donor Availability Stats">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={availabilityData} dataKey="value" nameKey="status" outerRadius={90} label>
              {availabilityData.map((_, idx) => <Cell key={idx} fill={pieColors[idx % pieColors.length]} />)}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Urgent Request Trends">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data.urgent_request_trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#b00020" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Top Cities by Donor Count">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.top_cities}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="city" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#1f8ea3" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
