import { useEffect, useState } from "react";

import LoadingSpinner from "../components/LoadingSpinner";
import { notificationService } from "../services";

export default function Notifications() {
  const [rows, setRows] = useState(null);

  useEffect(() => {
    notificationService.list().then(setRows);
  }, []);

  if (!rows) return <LoadingSpinner label="Loading notifications" />;

  return (
    <div className="card p-4">
      <h2 className="mb-3 text-lg font-semibold">Notification Center</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-2 py-2">ID</th>
              <th className="px-2 py-2">Donor</th>
              <th className="px-2 py-2">Request</th>
              <th className="px-2 py-2">Channel</th>
              <th className="px-2 py-2">Status</th>
              <th className="px-2 py-2">Sent At</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((n) => (
              <tr key={n.notification_id} className="border-t border-slate-100">
                <td className="px-2 py-2 text-xs">{n.notification_id.slice(0, 8)}...</td>
                <td className="px-2 py-2">{n.donor_id}</td>
                <td className="px-2 py-2">{n.request_id.slice(0, 8)}...</td>
                <td className="px-2 py-2 uppercase">{n.channel}</td>
                <td className="px-2 py-2">{n.sent_status}</td>
                <td className="px-2 py-2">{new Date(n.sent_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
