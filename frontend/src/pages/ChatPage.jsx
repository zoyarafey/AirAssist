import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import AirlineLogo from '../components/AirlineLogo'
import { BotMessage, UserMessage, TypingIndicator } from '../components/ChatMessage'

const WELCOME_MSG = {
  type: 'text',
  message: "Hello! 👋 Welcome to **Jahan Chatbot Airlines** support.\n\nI can help you with:\n- 🎫 **Book a flight** — Type \"book a flight\"\n- 📋 **View bookings** — Type \"my bookings\"\n- ❌ **Cancel booking** — Type \"cancel my flight\"\n- ✏️ **Update journey** — Type \"update my flight\"\n- 🧳 **Baggage policy** — Type \"baggage allowance\"\n\nHow can I assist you today?",
  id: 'welcome'
}

export default function ChatPage() {
  // FIX 2b: destructure updateUser from AuthContext
  const { user, logout, updateUser } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [messages, setMessages] = useState([WELCOME_MSG])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const initials = user?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'U'

  useEffect(() => {
    const initial = location.state?.initialMessage
    if (initial) {
      setTimeout(() => sendMessage(initial), 600)
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  const saveHistory = (msgs) => {
    try {
      const history = JSON.parse(sessionStorage.getItem(`airassist_history_${user?.customer_id}`) || '[]')
      const userMsgs = msgs.filter(m => m.role === 'user')
      if (userMsgs.length > 0) {
        const session = {
          lastMessage: userMsgs[userMsgs.length - 1]?.text,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          date: new Date().toLocaleDateString()
        }
        history.push(session)
        sessionStorage.setItem(`airassist_history_${user?.customer_id}`, JSON.stringify(history.slice(-20)))
      }
    } catch {}
  }

  const sendMessage = async (text) => {
    const msgText = (typeof text === 'string' ? text : input).trim()
    if (!msgText) return

    const userMsg = { role: 'user', text: msgText, initials, id: Date.now() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setTyping(true)

    try {
      const response = await api.chat(user.customer_id, msgText, {
        name: user.name,
        full_name: user.full_name || user.name,
        email: user.email,
        phone: user.phone,
        customer_id: user.customer_id
      })
      await new Promise(r => setTimeout(r, 600))
      setTyping(false)
      const botMsg = { ...response, role: 'bot', id: Date.now() + 1 }
      setMessages(prev => {
        const updated = [...prev, botMsg]
        saveHistory(updated)
        return updated
      })

      // FIX 2b: after profile update confirmed by bot, refresh user data from backend
      // Bot returns type:'text' with ✅ and mentions email/phone/name/address updated
      if (
        response.type === 'text' &&
        response.message?.includes('✅') &&
        (response.message?.includes('updated to') || response.message?.includes('has been updated'))
      ) {
        try {
          const freshUser = await api.getCustomer(user.customer_id)
          updateUser(freshUser)
        } catch {}
      }

    } catch (err) {
      setTyping(false)
      setMessages(prev => [...prev, {
        role: 'bot', type: 'text',
        message: '⚠️ Connection error. Please make sure the backend server is running at http://localhost:8000',
        id: Date.now() + 1
      }])
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const QUICK_CHIPS = [
    { label: '🎫 Book Flight', msg: 'book a flight' },
    { label: '📋 My Bookings', msg: 'my bookings' },
    { label: '❌ Cancel', msg: 'cancel my booking' },
    { label: '🧳 Baggage', msg: 'baggage allowance' },
    { label: '✏️ Update', msg: 'update my flight' },
    { label: '📜 Policies', msg: 'cancellation policy' },
  ]

  return (
    <div className="min-h-screen bg-animated flex flex-col">
      <nav className="glass-card border-b border-white/5 px-4 sm:px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/home')}
            className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-1.5">
            ← Home
          </button>
          <div className="w-px h-5 bg-white/10" />
          <AirlineLogo size="sm" />
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-xs text-gray-400 hidden sm:block">Support Online</span>
          </div>
          <button onClick={() => { logout(); navigate('/login') }}
            className="text-xs text-gray-500 hover:text-white transition-colors border border-white/10 px-3 py-1.5 rounded-lg">
            Sign out
          </button>
        </div>
      </nav>

      <div className="flex-1 flex flex-col lg:flex-row gap-0 max-w-7xl mx-auto w-full">
        {/* Left sidebar: passenger info — FIX 2b: reads from user state which updateUser keeps fresh */}
        <div className="lg:w-64 xl:w-72 flex-shrink-0 p-4 lg:p-6 hidden lg:block">
          <div className="glass-card rounded-2xl p-5 sticky top-24">
            <div className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-4">Passenger Info</div>
            <div className="flex items-center gap-3 mb-5">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-navy-600 to-sky-accent/40 border border-sky-accent/30 flex items-center justify-center text-white font-bold text-lg font-display">
                {initials}
              </div>
              <div>
                <div className="font-semibold text-white text-sm">{user?.full_name || user?.name}</div>
                <div className="text-xs text-sky-accent/70">{user?.customer_id}</div>
              </div>
            </div>
            <div className="space-y-3">
              {[
                { icon: '📧', label: 'Email', val: user?.email },
                { icon: '📱', label: 'Phone', val: user?.phone },
                { icon: '📍', label: 'Address', val: user?.address || 'Not provided' },
              ].map(({ icon, label, val }) => (
                <div key={label} className="bg-white/5 rounded-xl px-3 py-2.5">
                  <div className="text-[10px] text-gray-500 uppercase tracking-widest mb-0.5">{icon} {label}</div>
                  <div className="text-xs text-gray-300 break-all">{val}</div>
                </div>
              ))}
            </div>
            <div className="airline-stripe my-4 rounded-full" />
            <div className="text-[10px] text-gray-600 text-center">Need help? I'm here 24/7</div>
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 flex flex-col p-4 sm:p-6 min-h-0">
          <div className="flex gap-2 flex-wrap mb-4">
            {QUICK_CHIPS.map(chip => (
              <button key={chip.label} onClick={() => sendMessage(chip.msg)}
                className="text-xs bg-white/5 hover:bg-white/10 border border-white/10 hover:border-sky-accent/30 text-gray-300 px-3 py-1.5 rounded-full transition-all whitespace-nowrap">
                {chip.label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 pb-4" style={{ minHeight: '400px', maxHeight: 'calc(100vh - 340px)' }}>
            {messages.map((msg) =>
              msg.role === 'user'
                ? <UserMessage key={msg.id} msg={msg} />
                : <BotMessage key={msg.id} msg={msg} />
            )}
            {typing && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          <div className="mt-4 glass-card rounded-2xl p-2 flex items-end gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Enter to send)"
              rows={1}
              className="flex-1 bg-transparent resize-none px-3 py-2.5 text-sm text-white placeholder-gray-600 input-glow rounded-xl outline-none leading-relaxed"
              style={{ maxHeight: '120px' }}
              onInput={e => {
                e.target.style.height = 'auto'
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
              }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || typing}
              className="btn-primary text-white p-2.5 rounded-xl disabled:opacity-30 disabled:cursor-not-allowed flex-shrink-0 transition-all"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>
          <div className="text-center mt-2 text-[10px] text-gray-600">
            Jahan Chatbot Airlines • Support available 24/7 • Press Enter to send
          </div>
        </div>
      </div>
    </div>
  )
}
