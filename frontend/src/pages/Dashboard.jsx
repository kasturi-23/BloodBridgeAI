import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import LoadingSpinner from "../components/LoadingSpinner";
import StatusBadge from "../components/StatusBadge";
import SummaryCard from "../components/SummaryCard";
import { analyticsService, requestService } from "../services";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [requests, setRequests] = useState([]);

  const load = async () => {
    try {
      setLoading(true);
      setError("");
      const [analytics, requestRows] = await Promise.all([analyticsService.summary(), requestService.list()]);
      setMetrics(analytics.metrics);
      setRequests(requestRows.slice(0, 6));
    } catch (err) {
      setError(err?.response?.data?.detail || "Dashboard failed to load. Check backend server and API URL.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) return <LoadingSpinner label="Loading dashboard" />;
  if (error) {
    return (
      <div className="card p-5">
        <h2 className="text-base font-semibold text-red-700">Unable to load dashboard</h2>
        <p className="mt-2 text-sm text-slate-600">{error}</p>
        <button onClick={load} className="mt-4 rounded bg-primary px-4 py-2 text-sm font-semibold text-white">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <SummaryCard title="Total Donors" value={metrics.total_donors} />
        <SummaryCard title="Available Donors" value={metrics.available_donors} />
        <SummaryCard title="Eligible Donors" value={metrics.eligible_donors} />
        <SummaryCard title="Active Requests" value={metrics.active_requests} />
        <SummaryCard title="Urgent Alerts" value={metrics.urgent_request_alerts} subtitle="High + Critical pending" />
      </div>

      <div className="card p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-base font-semibold">Active Blood Requests</h2>
          <Link className="text-sm font-semibold text-primary" to="/requests/new">Create New Request</Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-2 py-2">Hospital</th>
                <th className="px-2 py-2">Blood Type</th>
                <th className="px-2 py-2">Urgency</th>
                <th className="px-2 py-2">Status</th>
                <th className="px-2 py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((req) => (
                <tr key={req.request_id} className="border-t border-slate-100">
                  <td className="px-2 py-2">{req.hospital_name}</td>
                  <td className="px-2 py-2">{req.blood_type_needed}</td>
                  <td className="px-2 py-2"><StatusBadge value={req.urgency_level} type="urgency" /></td>
                  <td className="px-2 py-2 capitalize">{req.status}</td>
                  <td className="px-2 py-2">
                    <Link className="text-primary" to={`/matches/${req.request_id}`}>View Matches</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
