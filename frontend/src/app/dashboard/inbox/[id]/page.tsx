'use client'

import { BackButton } from '@/shared/components/BackButton'

export default function InboxDetailPage() {
  return (
    <div className="space-y-6">
      <BackButton href="/dashboard/inbox" label="Back to inbox" />
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Conversation</h1>
        <p className="text-slate-600 mt-1">View conversation details</p>
      </div>
    </div>
  )
}
