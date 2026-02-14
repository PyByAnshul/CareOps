'use client'

import { useQuery } from '@tanstack/react-query'
import { bookingsApi } from '@/features/bookings/api/bookingsApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { Calendar, Plus, Eye } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

const statusColors = {
  confirmed: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  cancelled: 'bg-red-100 text-red-700',
  completed: 'bg-blue-100 text-blue-700',
}

export default function BookingsPage() {
  const [statusFilter, setStatusFilter] = useState('all')
  const { canRead, canWrite, isLoading: permLoading } = usePermissions()

  const { data: bookings = [], isLoading } = useQuery({
    queryKey: ['bookings', statusFilter],
    queryFn: () => bookingsApi.list({ status: statusFilter !== 'all' ? statusFilter : undefined }),
    enabled: canRead('bookings'),
  })

  if (permLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="bg-white rounded-lg border border-slate-200 p-6 h-64 animate-pulse" />
      </div>
    )
  }

  if (!canRead('bookings')) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Bookings</h1>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view bookings.
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-slate-900">Bookings</h1>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-slate-200 rounded animate-pulse"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Bookings</h1>
          <p className="text-slate-600 mt-1">Manage customer bookings</p>
        </div>
        {canWrite('bookings') && (
          <Link
            href="/dashboard/bookings/new"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Booking
          </Link>
        )}
      </div>

      <div className="flex gap-2">
        {['all', 'pending', 'confirmed', 'cancelled', 'completed'].map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              statusFilter === status
                ? 'bg-blue-600 text-white'
                : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Customer</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Service</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Date & Time</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Status</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {bookings.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center">
                  <Calendar className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-600">No bookings found</p>
                </td>
              </tr>
            ) : (
              bookings.map((booking: any) => (
                <tr key={booking.id} className="border-b border-slate-200 hover:bg-slate-50 transition-colors cursor-pointer"
                    onClick={() => window.location.href = `/dashboard/bookings/${booking.id}`}>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-slate-900">{booking.customer_name}</p>
                      <p className="text-sm text-slate-600">{booking.customer_email}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-900">{booking.service?.name || 'N/A'}</td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-slate-900">{new Date(booking.booking_date).toLocaleDateString()}</p>
                      <p className="text-sm text-slate-600">{booking.booking_time}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[booking.status as keyof typeof statusColors]}`}>
                      {booking.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <Link
                        href={`/dashboard/bookings/${booking.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
