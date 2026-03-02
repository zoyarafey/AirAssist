import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import AirlineLogo from '../components/AirlineLogo'

// FEATURE 1: Country list with codes for the dropdown
// When user picks a country, its code auto-fills the phone prefix
// User types only their local number after the pre-filled code
const COUNTRIES = [
  {name:"Afghanistan",code:"+93"},{name:"Albania",code:"+355"},{name:"Algeria",code:"+213"},
  {name:"Argentina",code:"+54"},{name:"Australia",code:"+61"},{name:"Austria",code:"+43"},
  {name:"Bangladesh",code:"+880"},{name:"Belgium",code:"+32"},{name:"Brazil",code:"+55"},
  {name:"Canada",code:"+1"},{name:"China",code:"+86"},{name:"Colombia",code:"+57"},
  {name:"Egypt",code:"+20"},{name:"Ethiopia",code:"+251"},{name:"France",code:"+33"},
  {name:"Germany",code:"+49"},{name:"Ghana",code:"+233"},{name:"Greece",code:"+30"},
  {name:"India",code:"+91"},{name:"Indonesia",code:"+62"},{name:"Iran",code:"+98"},
  {name:"Iraq",code:"+964"},{name:"Ireland",code:"+353"},{name:"Israel",code:"+972"},
  {name:"Italy",code:"+39"},{name:"Japan",code:"+81"},{name:"Jordan",code:"+962"},
  {name:"Kenya",code:"+254"},{name:"Malaysia",code:"+60"},{name:"Mexico",code:"+52"},
  {name:"Morocco",code:"+212"},{name:"Myanmar",code:"+95"},{name:"Nepal",code:"+977"},
  {name:"Netherlands",code:"+31"},{name:"New Zealand",code:"+64"},{name:"Nigeria",code:"+234"},
  {name:"Norway",code:"+47"},{name:"Pakistan",code:"+92"},{name:"Philippines",code:"+63"},
  {name:"Poland",code:"+48"},{name:"Portugal",code:"+351"},{name:"Qatar",code:"+974"},
  {name:"Romania",code:"+40"},{name:"Russia",code:"+7"},{name:"Saudi Arabia",code:"+966"},
  {name:"Singapore",code:"+65"},{name:"South Africa",code:"+27"},{name:"South Korea",code:"+82"},
  {name:"Spain",code:"+34"},{name:"Sri Lanka",code:"+94"},{name:"Sweden",code:"+46"},
  {name:"Switzerland",code:"+41"},{name:"Tanzania",code:"+255"},{name:"Thailand",code:"+66"},
  {name:"Turkey",code:"+90"},{name:"UAE",code:"+971"},{name:"Uganda",code:"+256"},
  {name:"Ukraine",code:"+380"},{name:"United Kingdom",code:"+44"},{name:"United States",code:"+1"},
  {name:"Vietnam",code:"+84"},{name:"Zimbabwe",code:"+263"}
]

export default function SignupPage() {
  const [form, setForm] = useState({ name: '', email: '', address: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // FEATURE 1: selectedCountry stores the chosen country object {name, code}
  // phoneLocal stores only the digits the user types (without country code)
  const [selectedCountry, setSelectedCountry] = useState(COUNTRIES.find(c => c.name === 'India'))
  const [phoneLocal, setPhoneLocal] = useState('')

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  // FEATURE 1: When country dropdown changes, update selectedCountry
  // The phone field value is always: selectedCountry.code + phoneLocal
  const handleCountryChange = (e) => {
    const country = COUNTRIES.find(c => c.name === e.target.value)
    if (country) setSelectedCountry(country)
  }

  // Full phone = country code + local number (what gets stored and validated)
  const fullPhone = selectedCountry.code + phoneLocal

  const handleSignup = async (e) => {
    e.preventDefault()
    setError('')

    // Email validation — unchanged
    const allowedEmailRegex = /^[^\s@]+@(gmail\.com|yahoo\.com|outlook\.com)$/i
    if (!allowedEmailRegex.test(form.email.trim())) {
      setError('Please enter a valid email address (example: name@gmail.com)')
      return
    }

    // FEATURE 1: Phone validation uses fullPhone (code + local digits)
    // Validation logic is UNCHANGED — same rules as before
    const phoneDigits = fullPhone.trim().startsWith('+') ? fullPhone.trim().slice(1) : null
    if (!phoneDigits || !/^\d{6,15}$/.test(phoneDigits)) {
      setError('Please enter a valid phone number with country code (example: +919876543210)')
      return
    }

    if (form.password !== form.confirm) { setError('Passwords do not match.'); return }
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }

    setLoading(true)
    try {
      // FEATURE 2: If address is blank, store the selected country name so
      // HomePage can show it as the display address (smart address logic)
      // We store a special marker "COUNTRY:<name>" so HomePage knows it's auto-filled
      // The user's real address field is NOT overwritten — this is stored as-is
      const addressToStore = form.address.trim()
        ? form.address.trim()
        : `COUNTRY:${selectedCountry.name}`

      // Pass selectedCountryName so backend/auth can store it for profile
      const data = await api.signup(form.name, form.email, fullPhone, form.password, addressToStore)
      login(data)
      navigate('/home')
    } catch (err) {
      setError(err.message || 'Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-animated flex items-center justify-center px-4 py-8">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full opacity-5" style={{background: 'radial-gradient(circle, #4db8ff, transparent)'}} />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full opacity-5" style={{background: 'radial-gradient(circle, #3560ad, transparent)'}} />
      </div>

      <div className="w-full max-w-md" style={{animation: 'slideUp 0.6s ease-out'}}>
        <div className="flex justify-center mb-6">
          <AirlineLogo size="md" />
        </div>

        <div className="glass-card rounded-3xl p-8">
          <h2 className="font-display text-xl font-bold text-white mb-1">Create Account</h2>
          <p className="text-gray-400 text-sm mb-6">Join Jahan Chatbot Airlines</p>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl px-4 py-3 text-sm mb-5">
              {error}
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">

              {/* Full Name — unchanged */}
              <div className="col-span-2">
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-2">Full Name</label>
                <input type="text" value={form.name} onChange={set('name')}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm input-glow transition-all"
                  placeholder="Amar Sharma" required />
              </div>

              {/* Email — unchanged */}
              <div className="col-span-2">
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-2">Email</label>
                <input type="text" value={form.email} onChange={set('email')}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm input-glow transition-all"
                  placeholder="you@gmail.com / yahoo.com / outlook.com" required />
                <p className="text-[11px] text-gray-600 mt-1 ml-1">Accepted: gmail.com · yahoo.com · outlook.com</p>
              </div>

              {/* FEATURE 1: Country dropdown + phone number input side by side
                  Dropdown selects country and auto-prefixes the code.
                  User types only their local number in the input box.
                  fullPhone = code + localNumber is what gets validated and stored. */}
              <div className="col-span-2">
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-2">Contact Number</label>
                <div className="flex gap-2">
                  {/* Country code dropdown */}
                  <select
                    value={selectedCountry.name}
                    onChange={handleCountryChange}
                    className="bg-white/5 border border-white/10 rounded-xl px-3 py-3 text-white text-sm input-glow transition-all w-40 flex-shrink-0"
                    style={{minWidth:'140px'}}
                  >
                    {COUNTRIES.map(c => (
                      <option key={c.name} value={c.name} style={{background:'#1a2744',color:'white'}}>
                        {c.code} {c.name}
                      </option>
                    ))}
                  </select>
                  {/* Local phone number — user types digits only, no country code needed */}
                  <input
                    type="tel"
                    value={phoneLocal}
                    onChange={e => setPhoneLocal(e.target.value.replace(/\D/g, ''))}
                    className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm input-glow transition-all"
                    placeholder="9876543210"
                    required
                  />
                </div>
                <p className="text-[11px] text-gray-600 mt-1 ml-1">
                  Select country · type local number · code auto-added ({selectedCountry.code})
                </p>
              </div>

              {/* Password with eye toggle — unchanged */}
              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-2">Password</label>
                <div className="relative">
                  <input type={showPassword ? 'text' : 'password'} value={form.password} onChange={set('password')}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pr-10 text-white placeholder-gray-600 text-sm input-glow transition-all"
                    placeholder="••••••••" required />
                  <button type="button" onClick={() => setShowPassword(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors" tabIndex={-1}>
                    {showPassword ? (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                        <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm password with eye toggle — unchanged */}
              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-2">Confirm</label>
                <div className="relative">
                  <input type={showConfirm ? 'text' : 'password'} value={form.confirm} onChange={set('confirm')}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pr-10 text-white placeholder-gray-600 text-sm input-glow transition-all"
                    placeholder="••••••••" required />
                  <button type="button" onClick={() => setShowConfirm(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors" tabIndex={-1}>
                    {showConfirm ? (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                        <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* Address — optional, unchanged */}
              <div className="col-span-2">
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-widest mb-2">
                  Address <span className="text-gray-600">(Optional)</span>
                </label>
                <input type="text" value={form.address} onChange={set('address')}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm input-glow transition-all"
                  placeholder="New Delhi, India" />
                <p className="text-[11px] text-gray-600 mt-1 ml-1">Leave blank to auto-fill your country name</p>
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="w-full btn-primary text-white font-semibold py-3 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed mt-2">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating account...
                </span>
              ) : 'Create Account'}
            </button>
          </form>

          <div className="airline-stripe my-6 rounded-full" />

          <p className="text-center text-sm text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="text-sky-accent hover:text-sky-300 font-medium transition-colors">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
