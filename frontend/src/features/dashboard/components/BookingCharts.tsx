'use client'

import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { dashboardApi } from '../api/dashboardApi'

const STATUS_COLORS = {
  pending: '#eab308',
  confirmed: '#22c55e',
  cancelled: '#ef4444',
  completed: '#3b82f6',
}

export function BookingCharts() {
  const { data, isLoading } = useQuery({
    queryKey: ['booking-stats'],
    queryFn: dashboardApi.getBookingStats,
  })

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-80 bg-slate-200 rounded-lg animate-pulse"></div>
        <div className="h-80 bg-slate-200 rounded-lg animate-pulse"></div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Bookings by Status - Pie Chart */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Bookings by Status</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data?.byStatus || []}
              dataKey="count"
              nameKey="status"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={(entry) => `${entry.status}: ${entry.count}`}
            >
              {(data?.byStatus || []).map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.status as keyof typeof STATUS_COLORS] || '#94a3b8'} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Bookings by Week - Bar Chart */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Bookings This Week</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data?.byWeek || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#3b82f6" name="Bookings" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
