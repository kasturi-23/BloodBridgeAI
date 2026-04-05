import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, Droplets, Clock } from 'lucide-react'
import { createRequest } from '../services/api'

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
const URGENCY_LEVELS = [
  { value: 'critical', label: 'Critical — Life threatening', color: 'text-red-700 bg-red-50 border-red-200' },
  { value: 'high', label: 'High — Needed within 1–2 hours', color: 'text-orange-700 bg-orange-50 border-orange-200' },
  { value: 'medium', label: 'Medium — Needed within 4–6 hours', color: 'text-yellow-700 bg-yellow-50 border-yellow-200' },
  { value: 'low', label: 'Low — Scheduled procedure', color: 'text-green-700 bg-green-50 border-green-200' },
]

export default function NewRequest() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    blood_group_needed: 'O+',
    units_needed: 1,
    urgency_level: 'high',
    required_by_time: '',
    notes: '',
    created_by: '',
  })

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const payload = {
        ...form,
        units_needed: Number(form.units_needed),
        required_by_time: form.required_by_time ? new Date(form.required_by_time).toISOString() : null,
      }
      const res = await createRequest(payload)
      navigate(`/request/${res.data.request_id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create request. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-red-100 p-2.5 rounded-xl">
          <AlertTriangle size={24} className="text-red-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">New Blood Request</h1>
          <p className="text-gray-500 text-sm">
            Create an urgent request — AI will immediately find and contact the best donors.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="card flex flex-col gap-6">
        {/* Blood Group */}
        <div>
          <label className="label">
            <Droplets size={14} className="inline mr-1 text-red-500" />
            Blood Group Required
          </label>
          <div className="grid grid-cols-4 gap-2 mt-2">
            {BLOOD_GROUPS.map((bg) => (
              <button
                key={bg}
                type="button"
                onClick={() => set('blood_group_needed', bg)}
                className={`py-3 rounded-lg font-bold text-sm border-2 transition-all ${
                  form.blood_group_needed === bg
                    ? 'border-red-600 bg-red-600 text-white shadow-md'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-red-300'
                }`}
              >
                {bg}
              </button>
            ))}
          </div>
        </div>

        {/* Units Needed */}
        <div>
          <label className="label">Units Needed</label>
          <input
            type="number"
            min="1"
            max="20"
            value={form.units_needed}
            onChange={(e) => set('units_needed', e.target.value)}
            className="input w-32"
            required
          />
          <p className="text-xs text-gray-400 mt-1">Number of blood units required</p>
        </div>

        {/* Urgency */}
        <div>
          <label className="label">Urgency Level</label>
          <div className="flex flex-col gap-2 mt-2">
            {URGENCY_LEVELS.map(({ value, label, color }) => (
              <label
                key={value}
                className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                  form.urgency_level === value
                    ? `${color} border-2`
                    : 'border-gray-200 bg-white hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="urgency"
                  value={value}
                  checked={form.urgency_level === value}
                  onChange={() => set('urgency_level', value)}
                  className="accent-red-600"
                />
                <span className="text-sm font-medium">{label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Required By Time */}
        <div>
          <label className="label">
            <Clock size={14} className="inline mr-1 text-gray-400" />
            Required By (optional)
          </label>
          <input
            type="datetime-local"
            value={form.required_by_time}
            onChange={(e) => set('required_by_time', e.target.value)}
            className="input"
          />
        </div>

        {/* Requesting Staff */}
        <div>
          <label className="label">Requesting Staff Name (optional)</label>
          <input
            type="text"
            value={form.created_by}
            onChange={(e) => set('created_by', e.target.value)}
            className="input"
            placeholder="Dr. Smith / Nurse Johnson"
          />
        </div>

        {/* Notes */}
        <div>
          <label className="label">Additional Notes (optional)</label>
          <textarea
            value={form.notes}
            onChange={(e) => set('notes', e.target.value)}
            rows={3}
            className="input resize-none"
            placeholder="Patient condition, ward number, any special requirements..."
          />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Submit */}
        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={loading} className="btn-primary flex-1 text-center">
            {loading ? 'Creating Request…' : 'Create Emergency Request'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
