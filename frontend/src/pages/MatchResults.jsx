import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import EmptyState from "../components/EmptyState";
import LoadingSpinner from "../components/LoadingSpinner";
import MatchCard from "../components/MatchCard";
import NotificationModal from "../components/NotificationModal";
import StatusBadge from "../components/StatusBadge";
import { notificationService, requestService } from "../services";

export default function MatchResults() {
  const { requestId } = useParams();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [selectedDonor, setSelectedDonor] = useState(null);
  const [selectedList, setSelectedList] = useState([]);

  const load = async () => {
    setLoading(true);
    const res = await requestService.matches(requestId);
    setData(res);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [requestId]);

  const onSelect = (match) => {
    setSelectedList((prev) => (prev.find((d) => d.donor_id === match.donor_id) ? prev : [...prev, match]));
  };

  const onGenerate = async (channel) => {
    const res = await notificationService.generate({
      donor_id: selectedDonor.donor_id,
      request_id: requestId,
      channel,
    });
    return res.generated_message;
  };

  const onSend = async (channel, message) => {
    await notificationService.send({
      donor_id: selectedDonor.donor_id,
      request_id: requestId,
      channel,
      generated_message: message,
    });
    await load();
  };

  if (loading) return <LoadingSpinner label="Generating donor matches" />;
  if (!data.matches.length) return <EmptyState title="No matches found" description="Try expanding search parameters or checking donor availability." />;

  return (
    <div className="space-y-4">
      <div className="card p-4">
        <h2 className="text-lg font-semibold">Match Results</h2>
        <p className="text-sm text-slate-500">{data.request.hospital_name} • {data.request.hospital_location}</p>
        <div className="mt-3 flex flex-wrap gap-3 text-sm">
          <p>Blood: <strong>{data.request.blood_type_needed}</strong></p>
          <p>Units: <strong>{data.request.units_required}</strong></p>
          <p>Urgency: <StatusBadge value={data.request.urgency_level} type="urgency" /></p>
          <p>Found: <strong>{data.total_matches} donors</strong></p>
          <p>Radius: <strong>{data.search_radius_miles} mi</strong></p>
        </div>
        <p className="mt-3 rounded-lg bg-primary/5 p-3 text-sm text-slate-700">AI Summary: {data.ai_summary}</p>
      </div>

      {!!selectedList.length && (
        <div className="card p-4">
          <h3 className="mb-2 font-semibold">Top Selected Donors</h3>
          <div className="flex flex-wrap gap-2">
            {selectedList.slice(0, 5).map((d) => (
              <span key={d.donor_id} className="rounded-full bg-emerald-100 px-3 py-1 text-xs text-emerald-700">{d.full_name}</span>
            ))}
          </div>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {data.matches.map((match) => (
          <MatchCard key={match.donor_id} match={match} requestId={requestId} onNotify={setSelectedDonor} onSelect={onSelect} />
        ))}
      </div>

      <NotificationModal
        open={!!selectedDonor}
        donor={selectedDonor}
        onClose={() => setSelectedDonor(null)}
        onGenerate={onGenerate}
        onSend={onSend}
      />
    </div>
  );
}
