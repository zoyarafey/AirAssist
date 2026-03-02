import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      // FIX: use sessionStorage instead of localStorage
      // localStorage persists across browser closes — user was never logged out
      // sessionStorage is automatically cleared when the tab/browser is closed
      // So every new session starts fresh at the login page
      const stored = sessionStorage.getItem('airassist_user')
      return stored ? JSON.parse(stored) : null
    } catch { return null }
  })

  const login = (userData) => {
    setUser(userData)
    // FIX: save to sessionStorage so session dies when browser closes
    sessionStorage.setItem('airassist_user', JSON.stringify(userData))
  }

  const updateUser = (updatedFields) => {
    const merged = { ...user, ...updatedFields }
    setUser(merged)
    // FIX: keep consistent — update sessionStorage, not localStorage
    sessionStorage.setItem('airassist_user', JSON.stringify(merged))
  }

  const logout = () => {
    setUser(null)
    // FIX: clear sessionStorage on manual logout too
    sessionStorage.removeItem('airassist_user')
    sessionStorage.removeItem('airassist_history')
  }

  return (
    <AuthContext.Provider value={{ user, login, updateUser, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
