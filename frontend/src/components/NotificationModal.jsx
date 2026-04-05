import { useState } from "react";

export default function NotificationModal({ open, donor, onClose, onGenerate, onSend }) {
  const [channel, setChannel] = useState("sms");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  if (!open || !donor) return null;

  const generate = async () => {
    setLoading(true);
    const generated = await onGenerate(channel);
    setMessage(generated);
    setLoading(false);
  };

  const send = async () => {
    setLoading(true);
    await onSend(channel, message);
    setLoading(false);
    setMessage("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-3">
      <div className="w-full max-w-lg rounded-xl bg-white p-5 shadow-xl">
        <h3 className="text-lg font-semibold">Notify {donor.full_name}</h3>
        <div className="mt-3 grid gap-3">
          <label className="text-sm">
            <span className="mb-1 block">Channel</span>
            <select className="w-full rounded border px-3 py-2" value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="sms">SMS</option>
              <option value="email">Email</option>
            </select>
          </label>
          <button disabled={loading} onClick={generate} className="rounded bg-primary px-3 py-2 text-sm text-white">
            {loading ? "Generating..." : "Generate AI Message"}
          </button>
          <textarea className="w-full rounded border px-3 py-2" rows="5" value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Generated message appears here..." />
          <div className="flex gap-2">
            <button disabled={loading || !message.trim()} onClick={send} className="rounded bg-accent px-3 py-2 text-sm text-white">Send (Simulated)</button>
            <button onClick={onClose} className="rounded bg-slate-100 px-3 py-2 text-sm">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  );
}
