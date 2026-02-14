'use client'

import { useAuth } from '@/core/auth/AuthProvider'
import { useRouter } from 'next/navigation'
import { Bell, LogOut, User, ChevronDown } from 'lucide-react'
import { useState } from 'react'

export function Header() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <header className="fixed top-0 right-0 left-64 h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 z-50">
      <div className="flex items-center gap-2">
        <h2 className="text-lg font-semibold text-slate-900">Workspace</h2>
      </div>

      <div className="flex items-center gap-4">
        {/* <button className="relative p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"> */}
          {/* <Bell className="w-5 h-5" /> */}
          {/* <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span> */}
        {/* </button> */}

        <div className="relative">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-2 p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">
              {user?.email?.[0].toUpperCase()}
            </div>
            <ChevronDown className="w-4 h-4 text-slate-600" />
          </button>

          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-slate-200 py-2 z-10">
              <div className="px-4 py-2 border-b border-slate-200">
                <p className="text-sm text-slate-900 font-medium">{user?.email}</p>
                <p className="text-xs text-slate-600 capitalize">{user?.role}</p>
              </div>
              <button
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 transition-colors"
                onClick={() => router.push('/dashboard/settings')}
              >
                <User className="w-4 h-4" />
                Profile Settings
              </button>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors border-t border-slate-200 mt-2 pt-2"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
