import { DashboardStats } from '@/features/dashboard/components/DashboardStats'
import { BookingCharts } from '@/features/dashboard/components/BookingCharts'
import { InventoryCharts } from '@/features/dashboard/components/InventoryCharts'

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-600 mt-2">Welcome back to your workspace</p>
      </div>

      <DashboardStats />

      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Booking Analytics</h2>
        <BookingCharts />
      </div>

      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Inventory Analytics</h2>
        <InventoryCharts />
      </div>
    </div>
  )
}
