<<<<<<< HEAD
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('[API Error]', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

// --- Requests ---
export const createRequest = (data) => api.post('/requests/', data)
export const listRequests = () => api.get('/requests/')
export const getRequest = (id) => api.get(`/requests/${id}`)
export const updateRequestStatus = (id, status) =>
  api.patch(`/requests/${id}/status`, { request_status: status })
export const triggerMatch = (id) => api.post(`/requests/${id}/match`)

// --- Donors ---
export const listDonors = (params) => api.get('/donors/', { params })
export const getDonor = (id) => api.get(`/donors/${id}`)
export const createDonor = (data) => api.post('/donors/', data)
export const updateDonor = (id, data) => api.patch(`/donors/${id}`, data)
export const deactivateDonor = (id) => api.delete(`/donors/${id}`)

// --- Dashboard ---
export const getDashboard = (requestId) => api.get(`/dashboard/${requestId}`)
export const listActiveRequests = () => api.get('/dashboard/')

// --- Calls ---
export const startOutreach = (requestId) => api.post(`/call/start/${requestId}`)
export const simulateCall = (callResponseId, data) =>
  api.post(`/call/simulate/${callResponseId}`, data)

// --- Config ---
export const getConfig = () => api.get('/config')

export default api
=======
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 10000,
});

export default api;
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
