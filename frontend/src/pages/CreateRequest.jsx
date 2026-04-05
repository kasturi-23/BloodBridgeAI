import { useState } from "react";
import { useNavigate } from "react-router-dom";

import RequestForm from "../components/RequestForm";
import { requestService } from "../services";

export default function CreateRequest() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (payload) => {
    try {
      setLoading(true);
      setError("");
      const req = await requestService.create(payload);
      navigate(`/matches/${req.request_id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create request");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Create Emergency Blood Request</h2>
      {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
      <RequestForm onSubmit={handleSubmit} loading={loading} />
    </div>
  );
}
