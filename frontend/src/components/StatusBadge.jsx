<<<<<<< HEAD
export function StatusBadge({ status }) {
  const map = {
    open:             { label: 'Open',             cls: 'bg-blue-100 text-blue-800' },
    in_progress:      { label: 'In Progress',      cls: 'bg-yellow-100 text-yellow-800' },
    donor_confirmed:  { label: 'Donor Confirmed',  cls: 'bg-green-100 text-green-800' },
    closed:           { label: 'Closed',           cls: 'bg-gray-100 text-gray-600' },
    failed:           { label: 'Failed',           cls: 'bg-red-100 text-red-700' },

    // Call statuses
    pending:          { label: 'Pending',          cls: 'bg-gray-100 text-gray-600' },
    calling:          { label: 'Calling…',         cls: 'bg-blue-100 text-blue-700' },
    accepted:         { label: 'Confirmed',        cls: 'bg-green-100 text-green-800' },
    declined:         { label: 'Declined',         cls: 'bg-red-100 text-red-700' },
    no_answer:        { label: 'No Answer',        cls: 'bg-orange-100 text-orange-700' },
    call_ended:       { label: 'Call Ended',       cls: 'bg-gray-100 text-gray-700' },
    ineligible:       { label: 'Ineligible',       cls: 'bg-purple-100 text-purple-700' },
    manual_review:    { label: 'Manual Review',    cls: 'bg-pink-100 text-pink-700' },
  }

  const { label, cls } = map[status] || { label: status, cls: 'bg-gray-100 text-gray-600' }
  return <span className={`badge ${cls}`}>{label}</span>
=======
import { donorStatusColors, urgencyColors } from "../utils/constants";

export default function StatusBadge({ value, type = "default" }) {
  const palette = type === "urgency" ? urgencyColors : donorStatusColors;
  return (
    <span className={`rounded-full px-2 py-1 text-xs font-semibold ${palette[value] || "bg-slate-100 text-slate-700"}`}>
      {value}
    </span>
  );
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
}
