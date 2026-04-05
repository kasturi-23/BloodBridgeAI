import { Link } from "react-router-dom";

import StatusBadge from "./StatusBadge";

export default function MatchCard({ match, requestId, onNotify, onSelect }) {
  return (
    <div className="card p-4">
      <div className="mb-2 flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-slate-800">{match.full_name}</h3>
          <p className="text-xs text-slate-500">{match.city} • {match.distance_miles} miles</p>
        </div>
        <span className="rounded-full bg-primary/10 px-2 py-1 text-xs font-semibold text-primary">{match.recommendation_tag}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
        <p>Blood: <strong>{match.blood_group}</strong></p>
        <p>Score: <strong>{(match.ranking_score * 100).toFixed(1)}%</strong></p>
        <p>Response: <strong>{Math.round(match.response_probability * 100)}%</strong></p>
        <p><StatusBadge value={match.availability_status} /></p>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <button onClick={() => onNotify(match)} className="rounded bg-accent px-3 py-1 text-xs font-semibold text-white">Notify Donor</button>
        <button onClick={() => onSelect(match)} className="rounded bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">Mark Selected</button>
        <Link to={`/donors/${match.donor_id}`} className="rounded bg-slate-100 px-3 py-1 text-xs">View Donor</Link>
      </div>
    </div>
  );
}
