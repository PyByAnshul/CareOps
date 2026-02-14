'use client'

import { ProtectedRoute } from '@/core/components/ProtectedRoute'
import { Sidebar } from '@/features/dashboard/components/Sidebar'
import { Header } from '@/features/dashboard/components/Header'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute>
      <div className="flex">
        <Sidebar />
        <div className="flex-1 ml-64">
          <Header />
          <main className="pt-16 pb-8 px-8 bg-slate-50 min-h-screen">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
