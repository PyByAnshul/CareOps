'use client'

import { BackButton } from '@/shared/components/BackButton'

export default function ServiceDetailPage() {
  return (
    <div className="space-y-6">
      <BackButton href="/dashboard/services" label="Back to services" />
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Service Details</h1>
        <p className="text-slate-600 mt-1">View service information</p>
      </div>
    </div>
  )
}
