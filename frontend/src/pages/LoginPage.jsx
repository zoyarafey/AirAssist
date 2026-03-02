import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import AirlineLogo from '../components/AirlineLogo'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // CHANGE 2: state to toggle password visibility on login page
  // Default false = hidden (dots). Click eye to show, click again to hide.
  const [showPassword, setShowPassword] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  // handleLogin is completely unchanged
  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.login(email, password)
      login(data)
      navigate('/home')
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-animated flex items-center justify-center px-4">
      {/* Background decorations — unchanged */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full opacity-5" style={{background: 'radial-gradient(circle, #4db8ff, transparent)'}} />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full opacity-5" style={{background: 'radial-gradient(circle, #3560ad, transparent)'}} />
        <div className="absolute top-1/4 left-1/4 text-white/3 text-9xl font-display select-none pointer-events-none">✈</div>
      </div>

      <div className="w-full max-w-md animate-slide-up" style={{animation: 'slideUp 0.6s ease-out'}}>
        {/* Logo area — unchanged */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <AirlineLogo size="lg" />
          </div>
          <p className="text-gray-400 text-sm tracking-wide">Customer Support Portal</p>
        </div>

        {/* Card — unchanged */}
        <div className="glass-card rounded-3xl p-8">
          <h2 className="font-display text-xl font-bold text-white mb-1">Welcome back</h2>
          <p className="text-gray-400 text-sm mb-6">Sign in to manage your flights</p>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl px-4 py-3 text-sm mb-5">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email field — unchanged */}
            <div>
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm input-glow transition-all"
                placeholder="you@example.com"
                required
              />
            </div>

            {/* CHANGE 2: Password field — wrapped in relative div, eye icon added inside */}
            {/* Only the wrapper div and eye button are new. Input className unchanged except pr-10 added for spacing. */}
            <div>
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pr-10 text-white placeholder-gray-600 text-sm input-glow transition-all"
                  placeholder="••••••••"
                  required
                />
                {/* Eye toggle button — only changes showPassword state, password value is unaffected */}
                <button
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    /* Eye-off: currently visible, click to hide */
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                      <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    /* Eye: currently hidden, click to show */
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary text-white font-semibold py-3 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed mt-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : 'Sign In'}
            </button>
          </form>

          <div className="airline-stripe my-6 rounded-full" />

          <p className="text-center text-sm text-gray-400">
            Don't have an account?{' '}
            <Link to="/signup" className="text-sky-accent hover:text-sky-300 font-medium transition-colors">
              Sign up
            </Link>
          </p>

          {/* Demo hint — unchanged */}
          <div className="mt-4 bg-navy-800/60 rounded-xl px-4 py-3 border border-white/5">
            <p className="text-xs text-gray-500 text-center">
              Demo: <span className="text-gray-400 font-mono">amar.sharma@email.com</span> / <span className="text-gray-400 font-mono">password123</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
