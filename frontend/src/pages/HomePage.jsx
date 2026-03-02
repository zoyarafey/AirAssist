import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import AirlineLogo from '../components/AirlineLogo'
import BoardingPass from '../components/BoardingPass'

export default function HomePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [chatHistory, setChatHistory] = useState([])
  const [bookings, setBookings] = useState([])
  const [loadingBookings, setLoadingBookings] = useState(true)
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 17 ? 'Good afternoon' : 'Good evening'
  const firstName = user?.name?.split(' ')[0] || 'Passenger'

  // FEATURE 2: Smart address display logic
  // If user left address blank during signup, we stored "COUNTRY:<name>" as a marker
  // Display shows the country name in that case — never shows the raw marker string
  // If user typed a real address, show it as-is. Do NOT overwrite stored data.
  const displayAddress = (() => {
    const addr = user?.address || ''
    if (addr.startsWith('COUNTRY:')) return addr.replace('COUNTRY:', '')
    return addr || '—'
  })()

  useEffect(() => {
    // Load chat history from localStorage
    try {
      const stored = sessionStorage.getItem(`airassist_history_${user?.customer_id}`)
      if (stored) setChatHistory(JSON.parse(stored))
    } catch {}

    // Load bookings
    if (user?.customer_id) {
      api.getBookings(user.customer_id)
        .then(res => setBookings(res.bookings || []))
        .catch(() => {})
        .finally(() => setLoadingBookings(false))
    }
  }, [user])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-animated flex flex-col">
      {/* Nav */}
      <nav className="glass-card border-b border-white/5 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <AirlineLogo size="sm" />
        <div className="flex items-center gap-4">
          <div className="text-right hidden sm:block">
            <div className="text-xs text-gray-400">{user?.email}</div>
            <div className="text-sm font-semibold text-white">{user?.name}</div>
          </div>
          <button onClick={handleLogout}
            className="text-xs text-gray-400 hover:text-white border border-white/10 hover:border-white/30 px-3 py-1.5 rounded-lg transition-all">
            Sign out
          </button>
        </div>
      </nav>

      <div className="flex-1 flex gap-6 p-6 max-w-7xl mx-auto w-full">
        {/* Left: Chat history */}
        <div className="w-72 flex-shrink-0 hidden lg:flex flex-col gap-4">
          {/* FEATURE 2: Passenger Info panel — shows smart address (country if blank, real address if entered) */}
          <div className="glass-card rounded-2xl p-5">
            <h3 className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-4">Passenger Info</h3>
            <div className="space-y-2">
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-widest">Name</div>
                <div className="text-sm font-semibold text-white">{user?.name || '—'}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-widest">Email</div>
                <div className="text-xs text-gray-300 break-all">{user?.email || '—'}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-widest">Phone</div>
                <div className="text-xs text-gray-300">{user?.phone || '—'}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-widest">Address</div>
                {/* displayAddress shows country name if address was left blank, real address otherwise */}
                <div className="text-xs text-gray-300">{displayAddress}</div>
              </div>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-5">
            <h3 className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-4">Chat History</h3>
            {chatHistory.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-3 opacity-30">💬</div>
                <p className="text-xs text-gray-500">No chats yet</p>
                <p className="text-xs text-gray-600 mt-1">Start a conversation</p>
              </div>
            ) : (
              <div className="space-y-2">
                {chatHistory.slice(-6).reverse().map((session, i) => (
                  <div key={i} className="bg-white/5 rounded-xl px-3 py-2 cursor-pointer hover:bg-white/10 transition-colors"
                    onClick={() => navigate('/chat')}>
                    <div className="text-xs text-gray-300 truncate">{session.lastMessage}</div>
                    <div className="text-[10px] text-gray-500 mt-1">{session.time}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick actions */}
          <div className="glass-card rounded-2xl p-5">
            <h3 className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {[
                { icon: '🎫', label: 'Book a Flight', msg: 'book a flight' },
                { icon: '📋', label: 'My Bookings', msg: 'my bookings' },
                { icon: '❌', label: 'Cancel Booking', msg: 'cancel my flight' },
                { icon: '🧳', label: 'Baggage Policy', msg: 'baggage allowance' },
              ].map((action, i) => (
                <button key={i}
                  onClick={() => navigate('/chat', { state: { initialMessage: action.msg } })}
                  className="w-full flex items-center gap-2.5 text-left bg-white/5 hover:bg-white/10 rounded-xl px-3 py-2 transition-all">
                  <span className="text-base">{action.icon}</span>
                  <span className="text-xs text-gray-300">{action.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Main content */}
        <div className="flex-1 space-y-6">
          {/* Welcome */}
          <div className="glass-card rounded-2xl p-6" style={{animation: 'slideUp 0.5s ease-out'}}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-sky-accent/70 mb-1">{greeting},</p>
                <h1 className="font-display text-3xl font-bold text-white">{firstName} ✈️</h1>
                <p className="text-gray-400 text-sm mt-2">Welcome to Jahan Chatbot Airlines support portal</p>
              </div>
              <div className="text-7xl opacity-10 select-none hidden sm:block">✈</div>
            </div>

            <button onClick={() => navigate('/chat')}
              className="mt-6 btn-primary text-white font-semibold py-3 px-8 rounded-xl text-sm inline-flex items-center gap-2">
              <span>💬</span> Start Chatting
            </button>
          </div>

          {/* Bookings */}
          <div className="glass-card rounded-2xl p-6" style={{animation: 'slideUp 0.6s ease-out'}}>
            <h2 className="text-sm font-medium text-gray-400 uppercase tracking-widest mb-4">Your Bookings</h2>
            {loadingBookings ? (
              <div className="flex items-center gap-3 py-4">
                <div className="w-5 h-5 border-2 border-sky-accent/30 border-t-sky-accent rounded-full animate-spin" />
                <span className="text-sm text-gray-400">Loading bookings...</span>
              </div>
            ) : bookings.length === 0 ? (
              <div className="text-center py-10">
                <div className="text-5xl mb-3 opacity-20">🎫</div>
                <p className="text-gray-400 text-sm">No bookings found</p>
                <button onClick={() => navigate('/chat', { state: { initialMessage: 'book a flight' } })}
                  className="mt-4 text-sky-accent text-sm hover:underline">
                  Book your first flight →
                </button>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {bookings.map((b, i) => (
                  <div key={i}><BoardingPass ticket={b} compact={true} /></div>
                ))}
              </div>
            )}
          </div>

          {/* Mobile quick actions */}
          <div className="glass-card rounded-2xl p-5 lg:hidden">
            <h3 className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-3">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { icon: '🎫', label: 'Book a Flight', msg: 'book a flight' },
                { icon: '📋', label: 'My Bookings', msg: 'my bookings' },
                { icon: '❌', label: 'Cancel Booking', msg: 'cancel my flight' },
                { icon: '🧳', label: 'Baggage Policy', msg: 'baggage allowance' },
              ].map((action, i) => (
                <button key={i}
                  onClick={() => navigate('/chat', { state: { initialMessage: action.msg } })}
                  className="flex items-center gap-2 text-left bg-white/5 hover:bg-white/10 rounded-xl px-3 py-3 transition-all">
                  <span>{action.icon}</span>
                  <span className="text-xs text-gray-300">{action.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
