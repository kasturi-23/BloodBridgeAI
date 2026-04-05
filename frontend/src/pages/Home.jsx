import { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { PlusCircle, RefreshCw, Clock, Droplets, AlertTriangle, CheckCircle } from 'lucide-react'
import { listRequests } from '../services/api'
import { StatusBadge } from '../components/StatusBadge'
import { usePolling } from '../hooks/usePolling'
import { format, formatDistanceToNow } from 'date-fns'

const URGENCY_BADGE = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700',
}

const STATUS_ICON = {
  open: <Clock size={16} className="text-blue-500" />,
  in_progress: <RefreshCw size={16} className="text-yellow-500 animate-spin" />,
  donor_confirmed: <CheckCircle size={16} className="text-green-500" />,
  failed: <AlertTriangle size={16} className="text-red-500" />,
  closed: <CheckCircle size={16} className="text-gray-400" />,
}

export default function Home() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchRequests = useCallback(async () => {
    try {
      const res = await listRequests()
      setRequests(res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  usePolling(fetchRequests, 8000, true)

  const active = requests.filter((r) =>
    ['open', 'in_progress', 'donor_confirmed'].includes(r.request_status)
  )
  const history = requests.filter((r) =>
    ['closed', 'failed'].includes(r.request_status)
  )

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Hero */}
      <div className="bg-gradient-to-br from-red-600 to-red-700 rounded-2xl p-8 mb-8 text-white shadow-lg">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">BloodBridge</h1>
            <p className="text-red-100 text-sm max-w-md">
              AI-powered emergency donor coordination. Create a request and the system
              automatically finds, verifies, and contacts the best donors.
            </p>
          </div>
          <Link
            to="/new-request"
            className="flex items-center gap-2 bg-white text-red-700 font-semibold px-5 py-2.5 rounded-xl hover:bg-red-50 transition-colors whitespace-nowrap shadow-sm"
          >
            <PlusCircle size={18} />
            New Request
          </Link>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          {[
            { label: 'Active Requests', value: active.length },
            { label: 'Total Requests', value: requests.length },
            { label: 'Confirmed Today', value: requests.filter(r => r.request_status === 'donor_confirmed').length },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white/10 rounded-xl px-4 py-3">
              <p className="text-2xl font-bold">{value}</p>
              <p className="text-red-100 text-xs">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Active requests */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full pulse-red inline-block" />
            Active Requests ({active.length})
          </h2>
          <button onClick={fetchRequests} className="text-gray-400 hover:text-gray-600">
            <RefreshCw size={15} />
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw size={24} className="animate-spin text-red-400" />
          </div>
        ) : active.length === 0 ? (
          <div className="card text-center py-12">
            <Droplets size={32} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 text-sm">No active requests</p>
            <Link to="/new-request" className="btn-primary mt-4 inline-flex items-center gap-2 text-sm">
              <PlusCircle size={14} /> Create First Request
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {active.map((req) => (
              <RequestRow key={req.request_id} req={req} />
            ))}
          </div>
        )}
      </section>

      {/* Request history */}
      {history.length > 0 && (
        <section>
          <h2 className="font-semibold text-gray-600 mb-4 text-sm uppercase tracking-wide">
            Request History
          </h2>
          <div className="flex flex-col gap-2">
            {history.map((req) => (
              <RequestRow key={req.request_id} req={req} muted />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

function RequestRow({ req, muted = false }) {
  return (
    <Link
      to={`/request/${req.request_id}`}
      className={`flex items-center gap-4 p-4 rounded-xl border transition-all hover:shadow-md ${
        muted
          ? 'bg-white border-gray-100 opacity-70 hover:opacity-100'
          : 'bg-white border-gray-100 hover:border-red-200'
      }`}
    >
      {/* Blood group */}
      <div className="bg-red-600 text-white font-bold text-sm px-3 py-2 rounded-lg min-w-[52px] text-center">
        {req.blood_group_needed}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-medium text-gray-900 text-sm">
            {req.units_needed} unit{req.units_needed > 1 ? 's' : ''} needed
          </span>
          <StatusBadge status={req.request_status} />
          <span className={`badge ${URGENCY_BADGE[req.urgency_level] || 'bg-gray-100 text-gray-600'}`}>
            {req.urgency_level}
          </span>
        </div>
        <div className="flex gap-3 text-xs text-gray-400 mt-0.5">
          <span>{formatDistanceToNow(new Date(req.created_at), { addSuffix: true })}</span>
          {req.created_by && <span>· {req.created_by}</span>}
          {req.notes && <span className="truncate max-w-xs">· {req.notes}</span>}
        </div>
      </div>

      {/* Status icon */}
      <div>{STATUS_ICON[req.request_status]}</div>
    </Link>
  )
}
