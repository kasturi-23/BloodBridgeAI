import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import LoadingSpinner from "../components/LoadingSpinner";
import StatusBadge from "../components/StatusBadge";
import { donorService } from "../services";

export default function DonorDetails() {
  const { donorId } = useParams();
  const [donor, setDonor] = useState(null);

  useEffect(() => {
    donorService.get(donorId).then(setDonor);
  }, [donorId]);

  if (!donor) return <LoadingSpinner label="Loading donor details" />;

  return (
    <div className="card p-5">
      <h2 className="text-lg font-semibold">{donor.full_name}</h2>
      <p className="text-sm text-slate-500">{donor.donor_id} • {donor.city}</p>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <p>Blood Group: <strong>{donor.blood_group}</strong></p>
        <p>Age: <strong>{donor.age}</strong></p>
        <p>Email: <strong>{donor.email}</strong></p>
        <p>Phone: <strong>{donor.phone}</strong></p>
        <p>Total Donations: <strong>{donor.total_donations}</strong></p>
        <p>Past Response Rate: <strong>{Math.round(donor.past_response_rate * 100)}%</strong></p>
        <p>Last Donation Date: <strong>{new Date(donor.last_donation_date).toLocaleDateString()}</strong></p>
        <p>Preferred Contact: <strong>{donor.preferred_contact_method.toUpperCase()}</strong></p>
        <p>Eligibility: <StatusBadge value={donor.eligibility_status} /></p>
        <p>Availability: <StatusBadge value={donor.availability_status} /></p>
        <p>Screening: <StatusBadge value={donor.health_screening_status} /></p>
        <p>Contacted/Responded: <strong>{donor.contacted ? "Yes" : "No"} / {donor.responded ? "Yes" : "No"}</strong></p>
      </div>
      {donor.notes && <p className="mt-4 rounded bg-slate-50 p-3 text-sm text-slate-700">{donor.notes}</p>}
    </div>
  );
}
