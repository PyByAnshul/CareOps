'use client'

import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../api/dashboardApi'
import { MetricCard } from './MetricCard'
import { Calendar, Clock, Mail, AlertTriangle } from 'lucide-react'
import { useAuth } from '@/core/auth/AuthProvider'

export function DashboardStats() {
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: dashboardApi.getSummary,
    enabled: isAuthenticated && !authLoading,
  })

  if (authLoading || isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-slate-200 rounded-lg animate-pulse"></div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 text-sm">Failed to load dashboard metrics</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        icon={Calendar}
        label="Bookings Today"
        value={data?.bookings_today || 0}
        link="/bookings"
        color="blue"
      />
      <MetricCard
        icon={Clock}
        label="Pending Bookings"
        value={data?.pending_bookings || 0}
        link="/bookings"
        color="yellow"
      />
      <MetricCard
        icon={Mail}
        label="Unread Messages"
        value={data?.unread_conversations || 0}
        link="/inbox"
        color="green"
      />
      <MetricCard
        icon={AlertTriangle}
        label="Active Alerts"
        value={data?.active_alerts || 0}
        link="/alerts"
        color="red"
      />
    </div>
  )
}
