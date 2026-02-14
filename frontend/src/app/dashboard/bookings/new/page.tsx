import { BookingForm } from '@/features/bookings/components/BookingForm'

export default function NewBookingPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">New Booking</h1>
        <p className="text-slate-600 mt-1">Create a new customer booking</p>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <BookingForm />
      </div>
    </div>
  )
}
