// FIX 1: Use relative /api URLs so Vite proxy handles CORS
// Previously used hardcoded 'http://localhost:8000' which fails on CORS-strict browsers
const BASE_URL = 'https://airassist.onrender.com'

async function apiCall(endpoint, method = 'GET', body = null) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 10000)

  try {
    const res = await fetch(endpoint, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : null,
      signal: controller.signal
    })
    
    clearTimeout(timeout)
  } catch (err) {
    clearTimeout(timeout)
    if (err.name === 'AbortError') {
      throw new Error('Request timed out. Please check your connection and try again.')
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
