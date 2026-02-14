'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { bookingsApi } from '../api/bookingsApi'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { apiClient } from '@/core/api/client'

const bookingSchema = z.object({
  service_id: z.number().min(1, 'Service is required'),
  customer_name: z.string().min(1, 'Customer name is required'),
  customer_email: z.string().email('Invalid email'),
  customer_phone: z.string().optional(),
  booking_date: z.string().min(1, 'Date is required'),
  booking_time: z.string().min(1, 'Time is required'),
  notes: z.string().optional(),
})

type BookingFormData = z.infer<typeof bookingSchema>

export function BookingForm({ initialData }: { initialData?: any }) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)

  const { data: services = [] } = useQuery({
    queryKey: ['services'],
    queryFn: async () => {
      const response = await apiClient.get('/api/services')
      return response.data
    },
  })

  const { register, handleSubmit, formState: { errors } } = useForm<BookingFormData>({
    resolver: zodResolver(bookingSchema),
    defaultValues: initialData,
  })

  const mutation = useMutation({
    mutationFn: (data: BookingFormData) => 
      initialData ? bookingsApi.update(initialData.id, data) : bookingsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] })
      router.push('/dashboard/bookings')
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to save booking')
    },
  })

  return (
    <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Service</label>
          <select
            {...register('service_id', { valueAsNumber: true })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">Select a service</option>
            {services.map((service: any) => (
              <option key={service.id} value={service.id}>
                {service.name} ({service.duration_minutes} min)
              </option>
            ))}
          </select>
          {errors.service_id && <p className="text-red-600 text-sm mt-1">{errors.service_id.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Customer Name</label>
          <input
            {...register('customer_name')}
            type="text"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          {errors.customer_name && <p className="text-red-600 text-sm mt-1">{errors.customer_name.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Customer Email</label>
          <input
            {...register('customer_email')}
            type="email"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          {errors.customer_email && <p className="text-red-600 text-sm mt-1">{errors.customer_email.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Customer Phone</label>
          <input
            {...register('customer_phone')}
            type="tel"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Booking Date</label>
          <input
            {...register('booking_date')}
            type="date"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          {errors.booking_date && <p className="text-red-600 text-sm mt-1">{errors.booking_date.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Booking Time</label>
          <input
            {...register('booking_time')}
            type="time"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          {errors.booking_time && <p className="text-red-600 text-sm mt-1">{errors.booking_time.message}</p>}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Notes</label>
        <textarea
          {...register('notes')}
          rows={4}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={mutation.isPending}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white px-6 py-2 rounded-lg transition-colors"
        >
          {mutation.isPending ? 'Saving...' : initialData ? 'Update Booking' : 'Create Booking'}
        </button>
        <button
          type="button"
          onClick={() => router.back()}
          className="bg-slate-200 hover:bg-slate-300 text-slate-900 px-6 py-2 rounded-lg transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
