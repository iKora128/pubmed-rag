'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, onAuthStateChanged, Auth } from 'firebase/auth'
import { getFirebaseAuth } from '@/lib/firebase/config'

interface AuthContextType {
  user: User | null
  loading: boolean
}

const AuthContext = createContext<AuthContextType>({ user: null, loading: true })

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [auth, setAuth] = useState<Auth | null>(null)

  useEffect(() => {
    const auth = getFirebaseAuth()
    setAuth(auth)
    const unsubscribe = onAuthStateChanged(auth, (authUser) => {
      setUser(authUser)
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const value: AuthContextType = {
    user,
    loading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}