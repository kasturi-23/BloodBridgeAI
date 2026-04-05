import { Link } from "react-router-dom";

import StatusBadge from "./StatusBadge";

export default function DonorTable({
  donors,
  onToggleAvailability,
  onToggleEligibility,
  onMarkContacted,
  onMarkResponded,
}) {
  return (
    <div className="card overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
          <tr>
            <th className="px-3 py-2">Donor</th>
            <th className="px-3 py-2">Blood</th>
            <th className="px-3 py-2">City</th>
            <th className="px-3 py-2">Eligibility</th>
            <th className="px-3 py-2">Availability</th>
            <th className="px-3 py-2">Response Rate</th>
            <th className="px-3 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {donors.map((d) => (
            <tr key={d.donor_id} className="border-t border-slate-100">
              <td className="px-3 py-2">
                <div className="font-semibold text-slate-800">{d.full_name}</div>
                <div className="text-xs text-slate-500">{d.donor_id}</div>
              </td>
              <td className="px-3 py-2">{d.blood_group}</td>
              <td className="px-3 py-2">{d.city}</td>
              <td className="px-3 py-2"><StatusBadge value={d.eligibility_status} /></td>
              <td className="px-3 py-2"><StatusBadge value={d.availability_status} /></td>
              <td className="px-3 py-2">{Math.round(d.past_response_rate * 100)}%</td>
              <td className="px-3 py-2">
                <div className="flex flex-wrap gap-2">
                  <Link to={`/donors/${d.donor_id}`} className="rounded bg-slate-100 px-2 py-1 text-xs">View</Link>
                  <button className="rounded bg-blue-100 px-2 py-1 text-xs text-blue-700" onClick={() => onToggleAvailability(d)}>
                    Toggle Availability
                  </button>
                  <button className="rounded bg-rose-100 px-2 py-1 text-xs text-rose-700" onClick={() => onToggleEligibility(d)}>
                    Toggle Eligibility
                  </button>
                  <button className="rounded bg-teal-100 px-2 py-1 text-xs text-teal-700" onClick={() => onMarkContacted(d)}>
                    Mark Contacted
                  </button>
                  <button className="rounded bg-emerald-100 px-2 py-1 text-xs text-emerald-700" onClick={() => onMarkResponded(d)}>
                    Mark Responded
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
