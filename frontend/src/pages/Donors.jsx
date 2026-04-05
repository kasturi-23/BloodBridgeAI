<<<<<<< HEAD
import { useState, useCallback } from 'react'
import { Users, Plus, Search, X, CheckCircle, AlertTriangle } from 'lucide-react'
import { listDonors, createDonor, updateDonor, deactivateDonor } from '../services/api'
import { usePolling } from '../hooks/usePolling'
import { format } from 'date-fns'

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

const BLOOD_COLORS = {
  'O-': 'bg-red-700', 'O+': 'bg-red-500',
  'A-': 'bg-blue-700', 'A+': 'bg-blue-500',
  'B-': 'bg-green-700', 'B+': 'bg-green-500',
  'AB-': 'bg-purple-700', 'AB+': 'bg-purple-500',
}

const STATUS_STYLES = {
  cleared:  'bg-green-100 text-green-700',
  pending:  'bg-yellow-100 text-yellow-700',
  failed:   'bg-red-100 text-red-700',
}

function AddDonorModal({ onClose, onSaved }) {
  const [form, setForm] = useState({
    full_name: '', phone_number: '', blood_group: 'O+',
    age: '', weight: '', address: '', latitude: '', longitude: '',
    screening_status: 'cleared', medication_flag: false,
    temporary_deferral_flag: false, availability_status: 'available',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function set(k, v) { setForm((f) => ({ ...f, [k]: v })) }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await createDonor({
        ...form,
        age: form.age ? Number(form.age) : null,
        weight: form.weight ? Number(form.weight) : null,
        latitude: form.latitude ? Number(form.latitude) : null,
        longitude: form.longitude ? Number(form.longitude) : null,
      })
      onSaved()
      onClose()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to add donor')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="font-bold text-lg">Add New Donor</h2>
          <button onClick={onClose}><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="label">Full Name</label>
              <input className="input" value={form.full_name} onChange={e => set('full_name', e.target.value)} required />
            </div>
            <div>
              <label className="label">Phone Number</label>
              <input className="input" value={form.phone_number} onChange={e => set('phone_number', e.target.value)} placeholder="+1234567890" required />
            </div>
            <div>
              <label className="label">Blood Group</label>
              <select className="input" value={form.blood_group} onChange={e => set('blood_group', e.target.value)}>
                {BLOOD_GROUPS.map(g => <option key={g}>{g}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Age</label>
              <input type="number" className="input" value={form.age} onChange={e => set('age', e.target.value)} min="17" max="65" />
            </div>
            <div>
              <label className="label">Weight (kg)</label>
              <input type="number" className="input" value={form.weight} onChange={e => set('weight', e.target.value)} min="50" />
            </div>
            <div className="col-span-2">
              <label className="label">Address</label>
              <input className="input" value={form.address} onChange={e => set('address', e.target.value)} />
            </div>
            <div>
              <label className="label">Latitude</label>
              <input type="number" step="any" className="input" value={form.latitude} onChange={e => set('latitude', e.target.value)} />
            </div>
            <div>
              <label className="label">Longitude</label>
              <input type="number" step="any" className="input" value={form.longitude} onChange={e => set('longitude', e.target.value)} />
            </div>
            <div>
              <label className="label">Screening Status</label>
              <select className="input" value={form.screening_status} onChange={e => set('screening_status', e.target.value)}>
                <option value="cleared">Cleared</option>
                <option value="pending">Pending</option>
                <option value="failed">Failed</option>
              </select>
            </div>
            <div className="flex flex-col gap-2 justify-end">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={form.medication_flag} onChange={e => set('medication_flag', e.target.checked)} className="accent-red-600" />
                Medication flag
              </label>
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={form.temporary_deferral_flag} onChange={e => set('temporary_deferral_flag', e.target.checked)} className="accent-red-600" />
                Temporary deferral
              </label>
            </div>
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Adding…' : 'Add Donor'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default function Donors() {
  const [donors, setDonors] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterGroup, setFilterGroup] = useState('')
  const [showAdd, setShowAdd] = useState(false)

  const fetchDonors = useCallback(async () => {
    try {
      const res = await listDonors({ blood_group: filterGroup || undefined })
      setDonors(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [filterGroup])

  usePolling(fetchDonors, 15000, true)

  async function toggleActive(donor) {
    if (donor.is_active) {
      await deactivateDonor(donor.donor_id)
    } else {
      await updateDonor(donor.donor_id, { is_active: true })
    }
    fetchDonors()
  }

  const filtered = donors.filter(d =>
    d.full_name.toLowerCase().includes(search.toLowerCase()) ||
    d.phone_number.includes(search)
  )

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {showAdd && <AddDonorModal onClose={() => setShowAdd(false)} onSaved={fetchDonors} />}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Users size={24} className="text-gray-700" />
          <h1 className="text-2xl font-bold text-gray-900">Donor Registry</h1>
          <span className="badge bg-gray-100 text-gray-600">{donors.length} donors</span>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2 text-sm">
          <Plus size={15} /> Add Donor
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            className="input pl-9"
            placeholder="Search by name or phone…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input w-auto"
          value={filterGroup}
          onChange={e => { setFilterGroup(e.target.value); }}
        >
          <option value="">All blood groups</option>
          {BLOOD_GROUPS.map(g => <option key={g}>{g}</option>)}
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <div className="card text-center py-12 text-gray-400">Loading donors…</div>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">No donors found</div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['Name', 'Blood', 'Phone', 'Location', 'Screening', 'Last Donated', 'Status', ''].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filtered.map(d => (
                <tr key={d.donor_id} className={`hover:bg-gray-50 ${!d.is_active ? 'opacity-50' : ''}`}>
                  <td className="px-4 py-3 font-medium text-gray-900">{d.full_name}</td>
                  <td className="px-4 py-3">
                    <span className={`${BLOOD_COLORS[d.blood_group] || 'bg-gray-500'} text-white text-xs font-bold px-2 py-0.5 rounded`}>
                      {d.blood_group}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{d.phone_number}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {d.latitude && d.longitude ? `${d.latitude.toFixed(4)}, ${d.longitude.toFixed(4)}` : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${STATUS_STYLES[d.screening_status] || 'bg-gray-100 text-gray-600'}`}>
                      {d.screening_status}
                    </span>
                    {d.medication_flag && <span className="ml-1 badge bg-orange-100 text-orange-600">Meds</span>}
                    {d.temporary_deferral_flag && <span className="ml-1 badge bg-purple-100 text-purple-600">Deferred</span>}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {d.last_donation_date ? format(new Date(d.last_donation_date), 'MMM d, yyyy') : 'Never'}
                  </td>
                  <td className="px-4 py-3">
                    {d.is_active
                      ? <span className="flex items-center gap-1 text-green-600 text-xs"><CheckCircle size={12}/>Active</span>
                      : <span className="flex items-center gap-1 text-gray-400 text-xs"><AlertTriangle size={12}/>Inactive</span>
                    }
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggleActive(d)}
                      className="text-xs text-gray-400 hover:text-gray-700 underline"
                    >
                      {d.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
=======
import { useEffect, useState } from "react";

import DonorTable from "../components/DonorTable";
import LoadingSpinner from "../components/LoadingSpinner";
import { donorService } from "../services";

export default function Donors() {
  const [loading, setLoading] = useState(true);
  const [donors, setDonors] = useState([]);
  const [filters, setFilters] = useState({ blood_group: "", city: "", eligibility: "", availability: "" });

  const load = async () => {
    setLoading(true);
    const rows = await donorService.list(filters);
    setDonors(rows);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const updateFilter = (key, value) => setFilters((prev) => ({ ...prev, [key]: value }));

  const applyFilter = () => load();

  const onToggleAvailability = async (donor) => {
    const next = donor.availability_status === "available" ? "unavailable" : "available";
    await donorService.update(donor.donor_id, { availability_status: next });
    load();
  };

  const onToggleEligibility = async (donor) => {
    const next = donor.eligibility_status === "eligible" ? "ineligible" : "eligible";
    await donorService.update(donor.donor_id, { eligibility_status: next });
    load();
  };

  const onMarkContacted = async (donor) => {
    await donorService.update(donor.donor_id, { contacted: true });
    load();
  };

  const onMarkResponded = async (donor) => {
    await donorService.update(donor.donor_id, { responded: true });
    load();
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Donor Management</h2>
      <div className="card grid gap-3 p-4 md:grid-cols-5">
        <input className="rounded border px-3 py-2 text-sm" placeholder="Blood Group" value={filters.blood_group} onChange={(e) => updateFilter("blood_group", e.target.value)} />
        <input className="rounded border px-3 py-2 text-sm" placeholder="City" value={filters.city} onChange={(e) => updateFilter("city", e.target.value)} />
        <select className="rounded border px-3 py-2 text-sm" value={filters.eligibility} onChange={(e) => updateFilter("eligibility", e.target.value)}>
          <option value="">Eligibility</option>
          <option value="eligible">eligible</option>
          <option value="ineligible">ineligible</option>
        </select>
        <select className="rounded border px-3 py-2 text-sm" value={filters.availability} onChange={(e) => updateFilter("availability", e.target.value)}>
          <option value="">Availability</option>
          <option value="available">available</option>
          <option value="unavailable">unavailable</option>
          <option value="busy">busy</option>
        </select>
        <button onClick={applyFilter} className="rounded bg-primary px-4 py-2 text-sm text-white">Apply Filters</button>
      </div>
      {loading ? (
        <LoadingSpinner label="Loading donors" />
      ) : (
        <DonorTable
          donors={donors}
          onToggleAvailability={onToggleAvailability}
          onToggleEligibility={onToggleEligibility}
          onMarkContacted={onMarkContacted}
          onMarkResponded={onMarkResponded}
        />
      )}
    </div>
  );
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
}
