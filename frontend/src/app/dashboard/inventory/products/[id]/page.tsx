'use client'

import { BackButton } from '@/shared/components/BackButton'

export default function ProductDetailPage() {
  return (
    <div className="space-y-6">
      <BackButton href="/dashboard/inventory" label="Back to inventory" />
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Product Details</h1>
        <p className="text-slate-600 mt-1">View product information</p>
      </div>
    </div>
  )
}
