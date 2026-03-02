// FIX 1: Use relative /api URLs so Vite proxy handles CORS
// Previously used hardcoded 'http://localhost:8000' which fails on CORS-strict browsers
const BASE_URL = 'https://airassist.onrender.com'

async function apiCall(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body) options.body = JSON.stringify(body)

  try {
    // FIX 1: prefix /api so Vite proxy forwards to http://localhost:8000
    const res = await fetch(`${BASE_URL}${endpoint}`, options)
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Server error' }))
      // FIX 1: throw the actual backend message, not a generic one
      throw new Error(err.detail || `Request failed (${res.status})`)
    }
    return res.json()
  } catch (err) {
    // FIX 1: distinguish network errors from backend errors
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Cannot connect to server. Make sure the backend is running on port 8000.')
    }
    throw err
  }
}

export const api = {
  login:       (email, password)                     => apiCall('/login',  'POST', { email, password }),
  signup:      (name, email, phone, password, address) => apiCall('/signup', 'POST', { name, email, phone, password, address }),
  chat:        (customer_id, message, customer_info)  => apiCall('/chat',   'POST', { customer_id, message, customer_info }),
  getBookings: (customer_id)                          => apiCall(`/bookings/${customer_id}`),
  getCustomer: (customer_id)                          => apiCall(`/customer/${customer_id}`),
}
