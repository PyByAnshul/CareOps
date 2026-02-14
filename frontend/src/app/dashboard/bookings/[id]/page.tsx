'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { bookingsApi } from '@/features/bookings/api/bookingsApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { useParams } from 'next/navigation'
import { Calendar, Mail, FileText, Clock, CheckCircle, XCircle, Check } from 'lucide-react'
import { BackButton } from '@/shared/components/BackButton'

export default function BookingDetailPage() {
  const params = useParams()
  const queryClient = useQueryClient()
  const { canRead, canWrite } = usePermissions()

  const { data: booking, isLoading } = useQuery({
    queryKey: ['booking', params.id],
    queryFn: () => bookingsApi.get(params.id as string),
    enabled: canRead('bookings'),
  })

  const confirmMutation = useMutation({
    mutationFn: () => bookingsApi.confirm(Number(params.id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', params.id] })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: () => bookingsApi.cancel(Number(params.id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', params.id] })
    },
  })

  const completeMutation = useMutation({
    mutationFn: () => bookingsApi.complete(Number(params.id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', params.id] })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse"></div>
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-12 bg-slate-200 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!canRead('bookings')) {
    return (
      <div className="space-y-6">
        <BackButton href="/dashboard/bookings" label="Back to bookings" />
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view this booking.
        </div>
      </div>
    )
  }

  if (!booking) return <div>Booking not found</div>

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'confirmed': return 'bg-green-100 text-green-800 border-green-300'
      case 'cancelled': return 'bg-red-100 text-red-800 border-red-300'
      case 'completed': return 'bg-blue-100 text-blue-800 border-blue-300'
      default: return 'bg-slate-100 text-slate-800 border-slate-300'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-5 h-5" />
      case 'confirmed': return <CheckCircle className="w-5 h-5" />
      case 'cancelled': return <XCircle className="w-5 h-5" />
      case 'completed': return <Check className="w-5 h-5" />
      default: return <Clock className="w-5 h-5" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3">
        <BackButton href="/dashboard/bookings" label="Back to bookings" />
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Booking Details</h1>
          <p className="text-slate-600 mt-1">Manage booking status and information</p>
        </div>
      </div>

      {/* Success Messages */}
      {confirmMutation.isSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-800">
          ✓ Booking confirmed! Confirmation email with calendar invite sent to customer.
        </div>
      )}
      {cancelMutation.isSuccess && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          ✓ Booking cancelled. Cancellation email sent to customer.
        </div>
      )}
      {completeMutation.isSuccess && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-blue-800">
          ✓ Booking marked as completed.
        </div>
      )}

      {/* Booking Details Container */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        {/* Status Bar with Action Buttons - Inside container at top */}
        <div className={`border-b-2 p-6 ${getStatusColor(booking.status)}`}>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              {getStatusIcon(booking.status)}
              <div>
                <p className="text-xs font-medium uppercase tracking-wide">Status</p>
                <p className="text-2xl font-bold capitalize">{booking.status}</p>
              </div>
            </div>
            
            {/* Action Buttons - only if write access */}
            {canWrite('bookings') && (
            <div className="flex flex-wrap gap-2">
              {booking.status === 'pending' && (
                <>
                  <button
                    onClick={() => confirmMutation.mutate()}
                    disabled={confirmMutation.isPending}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <CheckCircle className="w-4 h-4" />
                    {confirmMutation.isPending ? 'Confirming...' : 'Confirm'}
                  </button>
                  <button
                    onClick={() => cancelMutation.mutate()}
                    disabled={cancelMutation.isPending}
                    className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <XCircle className="w-4 h-4" />
                    {cancelMutation.isPending ? 'Cancelling...' : 'Cancel'}
                  </button>
                </>
              )}
              
              {booking.status === 'confirmed' && (
                <>
                  <button
                    onClick={() => completeMutation.mutate()}
                    disabled={completeMutation.isPending}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Check className="w-4 h-4" />
                    {completeMutation.isPending ? 'Completing...' : 'Complete'}
                  </button>
                  <button
                    onClick={() => cancelMutation.mutate()}
                    disabled={cancelMutation.isPending}
                    className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <XCircle className="w-4 h-4" />
                    {cancelMutation.isPending ? 'Cancelling...' : 'Cancel'}
                  </button>
                </>
              )}
            </div>
            )}
          </div>
        </div>

        {/* Booking Information */}
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-slate-600 mt-1" />
              <div>
                <p className="text-sm text-slate-600">Date & Time</p>
                <p className="font-medium text-slate-900">
                  {new Date(booking.booking_date).toLocaleDateString()} at {booking.booking_time}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <FileText className="w-5 h-5 text-slate-600 mt-1" />
              <div>
                <p className="text-sm text-slate-600">Service</p>
                <p className="font-medium text-slate-900">
                  {booking.service?.name || 'N/A'}
                  {booking.service?.duration_minutes && (
                    <span className="text-sm text-slate-600 ml-2">({booking.service.duration_minutes} min)</span>
                  )}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Mail className="w-5 h-5 text-slate-600 mt-1" />
              <div>
                <p className="text-sm text-slate-600">Customer Email</p>
                <p className="font-medium text-slate-900">{booking.customer_email}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Phone className="w-5 h-5 text-slate-600 mt-1" />
              <div>
                <p className="text-sm text-slate-600">Customer Name</p>
                <p className="font-medium text-slate-900">{booking.customer_name || 'N/A'}</p>
              </div>
            </div>
          </div>

          {booking.notes && (
            <div className="border-t border-slate-200 pt-6">
              <p className="text-sm text-slate-600 mb-2">Notes</p>
              <p className="text-slate-900">{booking.notes}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
