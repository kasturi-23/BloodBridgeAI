import { Phone, MapPin, Clock, Heart, AlertCircle, CheckCircle, XCircle, CalendarClock } from 'lucide-react'
import { StatusBadge } from './StatusBadge'
import { simulateCall } from '../services/api'
import { useState } from 'react'

const BLOOD_COLORS = {
  'O-': 'bg-red-600', 'O+': 'bg-red-500',
  'A-': 'bg-blue-600', 'A+': 'bg-blue-500',
  'B-': 'bg-green-600', 'B+': 'bg-green-500',
  'AB-': 'bg-purple-600', 'AB+': 'bg-purple-500',
}

export function DonorCard({ donor, callResponseId, onUpdate, showSimulate = false }) {
  const [loading, setLoading] = useState(false)

  const bloodColor = BLOOD_COLORS[donor.blood_group] || 'bg-gray-500'

  async function simulate(outcome) {
    if (!callResponseId) return
    setLoading(true)
    try {
      await simulateCall(callResponseId, {
        donor_id: donor.donor_id,
        call_status: outcome,
        eta_minutes: outcome === 'accepted' ? 20 : null,
        notes: outcome === 'declined' ? 'Simulated decline' : null,
      })
      onUpdate?.()
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const statusIcon = {
    accepted: <CheckCircle size={14} className="text-green-600" />,
    declined: <XCircle size={14} className="text-red-600" />,
    no_answer: <AlertCircle size={14} className="text-orange-500" />,
    ineligible: <AlertCircle size={14} className="text-purple-500" />,
  }[donor.call_status]

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex flex-col gap-3 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-3">
          <span className={`${bloodColor} text-white text-sm font-bold px-2.5 py-1 rounded-lg`}>
            {donor.blood_group}
          </span>
          <div>
            <p className="font-semibold text-gray-900">{donor.full_name}</p>
            <p className="text-xs text-gray-500">{donor.phone_number}</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {statusIcon}
          <StatusBadge status={donor.call_status} />
        </div>
      </div>

      {/* Info row */}
      <div className="flex flex-wrap gap-3 text-sm text-gray-600">
        {donor.distance_km != null && (
          <span className="flex items-center gap-1">
            <MapPin size={13} className="text-gray-400" />
            {donor.distance_km.toFixed(1)} km away
          </span>
        )}
        {donor.eta_minutes != null && (
          <span className="flex items-center gap-1">
            <Clock size={13} className="text-gray-400" />
            ETA: ~{donor.eta_minutes} min
          </span>
        )}
        {donor.fit_to_donate_today === true && (
          <span className="flex items-center gap-1 text-green-600">
            <Heart size={13} /> Fit to donate
          </span>
        )}
        {donor.fit_to_donate_today === false && (
          <span className="flex items-center gap-1 text-red-500">
            <Heart size={13} /> Not fit today
          </span>
        )}
        {donor.response_timestamp && (
          <span className="flex items-center gap-1 text-gray-400">
            <CalendarClock size={13} />
            {new Date(donor.response_timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>

      {/* Flags */}
      <div className="flex flex-wrap gap-2">
        {donor.map_sent && (
          <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full border border-green-100">
            Map sent
          </span>
        )}
        {donor.location_consent && (
          <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full border border-blue-100">
            Location shared
          </span>
        )}
        {donor.rank_position && (
          <span className="text-xs bg-gray-50 text-gray-600 px-2 py-0.5 rounded-full border border-gray-100">
            Rank #{donor.rank_position}
          </span>
        )}
      </div>

      {/* Ineligibility reason */}
      {donor.ineligibility_reason && (
        <p className="text-xs text-purple-600 bg-purple-50 px-3 py-1.5 rounded-lg">
          {donor.ineligibility_reason}
        </p>
      )}

      {/* Dev simulate buttons */}
      {showSimulate && (donor.call_status === 'pending' || donor.call_status === 'calling') && (
        <div className="flex gap-2 pt-1 border-t border-gray-50">
          <p className="text-xs text-gray-400 self-center mr-1">Simulate:</p>
          <button
            onClick={() => simulate('accepted')}
            disabled={loading}
            className="text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-lg disabled:opacity-50"
          >
            Accept
          </button>
          <button
            onClick={() => simulate('declined')}
            disabled={loading}
            className="text-xs bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-lg disabled:opacity-50"
          >
            Decline
          </button>
          <button
            onClick={() => simulate('no_answer')}
            disabled={loading}
            className="text-xs bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded-lg disabled:opacity-50"
          >
            No Answer
          </button>
        </div>
      )}
    </div>
  )
}
