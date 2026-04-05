import { useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, RefreshCw, Phone, CheckCircle2,
  Clock, Users, AlertTriangle, MapPin, Play
} from 'lucide-react'
import { getDashboard, updateRequestStatus, startOutreach, triggerMatch } from '../services/api'
import { StatusBadge } from '../components/StatusBadge'
import { DonorCard } from '../components/DonorCard'
import { usePolling } from '../hooks/usePolling'
import { format } from 'date-fns'

const URGENCY_COLOR = {
  critical: 'text-red-700 bg-red-50',
  high: 'text-orange-700 bg-orange-50',
  medium: 'text-yellow-700 bg-yellow-50',
  low: 'text-green-700 bg-green-50',
}

function StatCard({ icon: Icon, label, value, color = 'text-gray-900' }) {
  return (
    <div className="card flex items-center gap-4">
      <div className="bg-gray-50 p-3 rounded-xl">
        <Icon size={20} className="text-gray-500" />
      </div>
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
        <p className={`text-2xl font-bold ${color}`}>{value}</p>
      </div>
    </div>
  )
}

export default function RequestDashboard() {
  const { requestId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchDashboard = useCallback(async () => {
    try {
      const res = await getDashboard(requestId)
      setData(res.data)
      setError('')
    } catch (e) {
      setError('Failed to load dashboard. Retrying…')
    } finally {
      setLoading(false)
    }
  }, [requestId])

  // Is request still live?
  const isLive = data?.request?.request_status &&
    ['open', 'in_progress'].includes(data.request.request_status)

  usePolling(fetchDashboard, 5000, true)

  async function handleClose() {
    setActionLoading(true)
    try {
      await updateRequestStatus(requestId, 'closed')
      fetchDashboard()
    } finally {
      setActionLoading(false)
    }
  }

  async function handleStartOutreach() {
    setActionLoading(true)
    try {
      await startOutreach(requestId)
      fetchDashboard()
    } finally {
      setActionLoading(false)
    }
  }

  async function handleReTriggerMatch() {
    setActionLoading(true)
    try {
      await triggerMatch(requestId)
      setTimeout(fetchDashboard, 2000)
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw size={24} className="animate-spin text-red-500" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <div className="card text-center">
          <AlertTriangle size={32} className="mx-auto text-red-500 mb-3" />
          <p className="text-gray-600">{error || 'Request not found.'}</p>
          <Link to="/" className="btn-secondary mt-4 inline-block">Back to Dashboard</Link>
        </div>
      </div>
    )
  }

  const { request, confirmed_donors, standby_donors, pending_donors, declined_donors, total_donors_contacted } = data

  // Build call response ID lookup from declined/pending cards
  const allDonors = [...pending_donors, ...declined_donors, ...standby_donors]
  const getCallId = (donor) => donor.call_response_id

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Back + Live indicator */}
      <div className="flex items-center gap-4 mb-6">
        <Link to="/" className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm">
          <ArrowLeft size={15} /> All Requests
        </Link>
        {isLive && (
          <span className="flex items-center gap-1.5 text-xs text-red-600 font-medium">
            <span className="w-2 h-2 bg-red-500 rounded-full pulse-red inline-block" />
            Live — refreshing every 5s
          </span>
        )}
        <button onClick={fetchDashboard} className="ml-auto text-gray-400 hover:text-gray-600">
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Request header */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="bg-red-600 text-white font-bold text-xl px-4 py-3 rounded-xl min-w-[64px] text-center">
              {request.blood_group_needed}
            </div>
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h1 className="text-xl font-bold text-gray-900">
                  {request.units_needed} unit{request.units_needed > 1 ? 's' : ''} of {request.blood_group_needed}
                </h1>
                <StatusBadge status={request.request_status} />
                <span className={`badge ${URGENCY_COLOR[request.urgency_level] || 'bg-gray-100 text-gray-600'}`}>
                  {request.urgency_level?.toUpperCase()}
                </span>
              </div>
              <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <MapPin size={13} /> {request.hospital_name}
                </span>
                {request.required_by_time && (
                  <span className="flex items-center gap-1">
                    <Clock size={13} /> Due: {format(new Date(request.required_by_time), 'MMM d, h:mm a')}
                  </span>
                )}
                <span>Created: {format(new Date(request.created_at), 'MMM d, h:mm a')}</span>
                {request.created_by && <span>By: {request.created_by}</span>}
              </div>
              {request.notes && (
                <p className="mt-2 text-sm text-gray-600 bg-gray-50 px-3 py-1.5 rounded-lg">
                  {request.notes}
                </p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-2">
            {(request.request_status === 'open' || request.request_status === 'in_progress') && (
              <>
                <button
                  onClick={handleStartOutreach}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 btn-primary text-sm"
                >
                  <Play size={14} /> Call Next Donor
                </button>
                <button
                  onClick={handleReTriggerMatch}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 btn-secondary text-sm"
                >
                  <RefreshCw size={14} /> Re-match
                </button>
                <button
                  onClick={handleClose}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 btn-secondary text-sm text-gray-500"
                >
                  Close Request
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard icon={CheckCircle2} label="Confirmed" value={confirmed_donors.length} color="text-green-700" />
        <StatCard icon={Users} label="Units Needed" value={request.units_needed} />
        <StatCard icon={Phone} label="Contacted" value={total_donors_contacted} />
        <StatCard icon={Users} label="Standby" value={standby_donors.length} color="text-blue-700" />
      </div>

      {/* Donor sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confirmed */}
        <section>
          <h2 className="text-sm font-semibold text-green-700 uppercase tracking-wide mb-3 flex items-center gap-1">
            <CheckCircle2 size={14} /> Confirmed Donors ({confirmed_donors.length})
          </h2>
          {confirmed_donors.length === 0 ? (
            <div className="bg-gray-50 border border-gray-100 rounded-xl p-6 text-center text-gray-400 text-sm">
              No confirmed donors yet
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {confirmed_donors.map((d) => (
                <DonorCard
                  key={d.donor_id}
                  donor={d}
                  callResponseId={d.call_response_id}
                  onUpdate={fetchDashboard}
                />
              ))}
            </div>
          )}
        </section>

        {/* Pending / Calling */}
        <section>
          <h2 className="text-sm font-semibold text-blue-700 uppercase tracking-wide mb-3 flex items-center gap-1">
            <Phone size={14} /> In Queue ({pending_donors.length})
          </h2>
          {pending_donors.length === 0 ? (
            <div className="bg-gray-50 border border-gray-100 rounded-xl p-6 text-center text-gray-400 text-sm">
              No donors pending
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {pending_donors.map((d) => (
                <DonorCard
                  key={d.donor_id}
                  donor={d}
                  callResponseId={d.call_response_id}
                  onUpdate={fetchDashboard}
                  showSimulate
                />
              ))}
            </div>
          )}
        </section>

        {/* Standby */}
        {standby_donors.length > 0 && (
          <section>
            <h2 className="text-sm font-semibold text-purple-700 uppercase tracking-wide mb-3">
              Standby Donors ({standby_donors.length})
            </h2>
            <div className="flex flex-col gap-3">
              {standby_donors.map((d) => (
                <DonorCard key={d.donor_id} donor={d} onUpdate={fetchDashboard} />
              ))}
            </div>
          </section>
        )}

        {/* Declined / No Answer / Ineligible */}
        {declined_donors.length > 0 && (
          <section>
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Declined / No Answer / Ineligible ({declined_donors.length})
            </h2>
            <div className="flex flex-col gap-3">
              {declined_donors.map((d) => (
                <DonorCard key={d.donor_id} donor={d} onUpdate={fetchDashboard} />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}
