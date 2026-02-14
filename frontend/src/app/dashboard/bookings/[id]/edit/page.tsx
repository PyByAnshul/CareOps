'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, Trash2, Calendar, User, Mail, Clock, CheckCircle, XCircle, Check } from 'lucide-react'
import { bookingsApi } from '@/features/bookings/api/bookingsApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { BackButton } from '@/shared/components/BackButton'

export default function EditBookingPage() {
  const router = useRouter()
  const params = useParams()
  const bookingId = params.id as string
  const queryClient = useQueryClient()
  const { canRead, canWrite, canDelete } = usePermissions()

  const [formData, setFormData] = useState({
    customer_name: '',
    customer_email: '',
    booking_date: '',
    booking_time: '',
    notes: ''
  })
  const [isSaving, setIsSaving] = useState(false)

  const { data: booking, isLoading } = useQuery({
    queryKey: ['booking', bookingId],
    queryFn: () => bookingsApi.get(bookingId),
    enabled: canRead('bookings'),
  })

  const confirmMutation = useMutation({
    mutationFn: () => bookingsApi.confirm(Number(bookingId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', bookingId] })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: () => bookingsApi.cancel(Number(bookingId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', bookingId] })
    },
  })

  const completeMutation = useMutation({
    mutationFn: () => bookingsApi.complete(Number(bookingId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', bookingId] })
    },
  })

  useEffect(() => {
    if (booking) {
      setFormData({
        customer_name: booking.customer_name || '',
        customer_email: booking.customer_email || '',
        booking_date: booking.booking_date || '',
        booking_time: booking.booking_time || '',
        notes: booking.notes || ''
      })
    }
  }, [booking])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await bookingsApi.update(bookingId, formData)
      router.push('/dashboard/bookings')
    } catch (error) {
      console.error('Failed to update booking:', error)
      alert('Failed to update booking')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this booking?')) {
      try {
        await bookingsApi.delete(bookingId)
        router.push('/dashboard/bookings')
      } catch (error) {
        console.error('Failed to delete booking:', error)
        alert('Failed to delete booking')
      }
    }
  }

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

  if (isLoading) {
    return (
      <div className="h-full bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!canRead('bookings')) {
    return (
      <div className="h-full bg-slate-50 p-6">
        <BackButton href="/dashboard/bookings" label="Back to bookings" />
        <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to edit bookings.
        </div>
      </div>
    )
  }

  if (!booking) {
    return (
      <div className="h-full bg-slate-50 flex items-center justify-center">
        <p className="text-slate-600">Booking not found</p>
      </div>
    )
  }

  return (
    <div className="h-full bg-slate-50">
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <BackButton href="/dashboard/bookings" label="Back to bookings" />
            <div>
              <h1 className="text-xl font-semibold text-slate-900">Edit Booking</h1>
              <p className="text-sm text-slate-600">Modify booking details</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {canDelete('bookings') && (
              <button onClick={handleDelete} className="flex items-center px-3 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </button>
            )}
            {canWrite('bookings') && (
              <button onClick={handleSave} disabled={isSaving} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                <Save className="w-4 h-4 mr-2" />
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="max-w-2xl mx-auto">
          {/* Status Bar with Action Buttons - only if write access */}
          {booking && canWrite('bookings') && (
            <div className={`rounded-lg border-2 p-4 mb-6 ${getStatusColor(booking.status)}`}>
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  {getStatusIcon(booking.status)}
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide">Status</p>
                    <p className="text-xl font-bold capitalize">{booking.status}</p>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-2">
                  {booking.status === 'pending' && (
                    <>
                      <button
                        onClick={() => confirmMutation.mutate()}
                        disabled={confirmMutation.isPending}
                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 text-sm"
                      >
                        <CheckCircle className="w-4 h-4" />
                        {confirmMutation.isPending ? 'Confirming...' : 'Confirm'}
                      </button>
                      <button
                        onClick={() => cancelMutation.mutate()}
                        disabled={cancelMutation.isPending}
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 text-sm"
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
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 text-sm"
                      >
                        <Check className="w-4 h-4" />
                        {completeMutation.isPending ? 'Completing...' : 'Complete'}
                      </button>
                      <button
                        onClick={() => cancelMutation.mutate()}
                        disabled={cancelMutation.isPending}
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 text-sm"
                      >
                        <XCircle className="w-4 h-4" />
                        {cancelMutation.isPending ? 'Cancelling...' : 'Cancel'}
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Service
                </label>
                <div className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700">
                  {booking.service?.name || 'N/A'}
                  {booking.service?.duration_minutes && (
                    <span className="text-sm text-slate-600 ml-2">({booking.service.duration_minutes} min)</span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-1">Service cannot be changed after booking is created</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <User className="w-4 h-4 inline mr-2" />
                  Customer Name
                </label>
                <input
                  type="text"
                  value={formData.customer_name}
                  onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Customer Email
                </label>
                <input
                  type="email"
                  value={formData.customer_email}
                  onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Calendar className="w-4 h-4 inline mr-2" />
                  Booking Date
                </label>
                <input
                  type="date"
                  value={formData.booking_date}
                  onChange={(e) => setFormData({ ...formData, booking_date: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Booking Time</label>
                <input
                  type="time"
                  value={formData.booking_time}
                  onChange={(e) => setFormData({ ...formData, booking_time: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}