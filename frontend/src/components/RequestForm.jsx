import { useState } from "react";

const initial = {
  hospital_name: "",
  hospital_location: "",
  hospital_latitude: "",
  hospital_longitude: "",
  contact_person: "",
  blood_type_needed: "O-",
  units_required: 1,
  urgency_level: "High",
  required_within_hours: 3,
  notes: "",
};

const bloodTypes = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"];

export default function RequestForm({ onSubmit, loading }) {
  const [form, setForm] = useState(initial);

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      hospital_latitude: Number(form.hospital_latitude),
      hospital_longitude: Number(form.hospital_longitude),
      units_required: Number(form.units_required),
      required_within_hours: Number(form.required_within_hours),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-4 p-5">
      <div className="grid gap-4 md:grid-cols-2">
        {[
          ["hospital_name", "Hospital Name"],
          ["hospital_location", "Hospital City"],
          ["contact_person", "Contact Person"],
          ["hospital_latitude", "Hospital Latitude"],
          ["hospital_longitude", "Hospital Longitude"],
        ].map(([key, label]) => (
          <label key={key} className="text-sm">
            <span className="mb-1 block font-medium text-slate-700">{label}</span>
            <input
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={form[key]}
              onChange={(e) => update(key, e.target.value)}
            />
          </label>
        ))}
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Blood Type Needed</span>
          <select className="w-full rounded-lg border border-slate-300 px-3 py-2" value={form.blood_type_needed} onChange={(e) => update("blood_type_needed", e.target.value)}>
            {bloodTypes.map((bg) => (
              <option key={bg}>{bg}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Urgency</span>
          <select className="w-full rounded-lg border border-slate-300 px-3 py-2" value={form.urgency_level} onChange={(e) => update("urgency_level", e.target.value)}>
            {["Low", "Medium", "High", "Critical"].map((u) => (
              <option key={u}>{u}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Units Required</span>
          <input required type="number" min="1" className="w-full rounded-lg border border-slate-300 px-3 py-2" value={form.units_required} onChange={(e) => update("units_required", e.target.value)} />
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Required Within (hours)</span>
          <input required type="number" min="1" className="w-full rounded-lg border border-slate-300 px-3 py-2" value={form.required_within_hours} onChange={(e) => update("required_within_hours", e.target.value)} />
        </label>
      </div>
      <label className="block text-sm">
        <span className="mb-1 block font-medium text-slate-700">Notes</span>
        <textarea className="w-full rounded-lg border border-slate-300 px-3 py-2" rows="3" value={form.notes} onChange={(e) => update("notes", e.target.value)} />
      </label>
      <button disabled={loading} className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
        {loading ? "Creating..." : "Create Request & Run Matching"}
      </button>
    </form>
  );
}
