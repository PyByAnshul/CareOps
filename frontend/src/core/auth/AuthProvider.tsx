'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { jwtDecode } from 'jwt-decode'
import Cookies from 'js-cookie'

export interface User {
  id: number
  email: string
  role: string
  workspace_id: number
}

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (token: string) => void
  logout: () => void
  setUser: (user: User | null) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize auth state from cookies
  useEffect(() => {
    const savedToken = Cookies.get('auth_token')
    if (savedToken) {
      try {
        const decoded = jwtDecode<any>(savedToken)
        setToken(savedToken)
        setUser({
          id: parseInt(decoded.sub) || decoded.user_id,
          email: decoded.email,
          role: decoded.role || 'staff',
          workspace_id: decoded.workspace_id,
        })
      } catch (error) {
        Cookies.remove('auth_token')
      }
    }
    setIsLoading(false)
  }, [])

  const login = (newToken: string) => {
    try {
      const decoded = jwtDecode<any>(newToken)
      const newUser: User = {
        id: parseInt(decoded.sub) || decoded.user_id,
        email: decoded.email,
        role: decoded.role || 'staff',
        workspace_id: decoded.workspace_id,
      }
      
      setToken(newToken)
      setUser(newUser)
      Cookies.set('auth_token', newToken, { expires: 7 })
      console.log('Token saved to cookie')
    } catch (error) {
      console.error('Failed to decode token:', error)
    }
  }

  const logout = () => {
    Cookies.remove('auth_token')
    setToken(null)
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    logout,
    setUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
