'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { inboxApi } from '@/features/inbox/api/inboxApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { useState } from 'react'
import { Mail, Search, RefreshCw } from 'lucide-react'
import { MessageThread } from '@/features/inbox/components/MessageThread'
import { ConversationList } from '@/features/inbox/components/ConversationList'

export default function InboxPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState('all')
  const [search, setSearch] = useState('')
  const queryClient = useQueryClient()
  const { canRead, canWrite, isLoading: permLoading } = usePermissions()

  const { data: conversations = [], isLoading } = useQuery({
    queryKey: ['conversations', statusFilter],
    queryFn: () => inboxApi.getConversations({ status: statusFilter !== 'all' ? statusFilter : undefined }),
    enabled: canRead('inbox'),
  })

  const syncMutation = useMutation({
    mutationFn: inboxApi.syncGmail,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      alert(`✅ Synced ${data.synced} new emails out of ${data.total} total emails`)
    },
    onError: (error: any) => {
      alert(`❌ Sync failed: ${error.response?.data?.detail || error.message}`)
    },
  })

  const filtered = conversations.filter((c: any) => {
    const searchLower = search.toLowerCase()
    return (
      c.contact_email?.toLowerCase().includes(searchLower) ||
      c.customer_name?.toLowerCase().includes(searchLower) ||
      c.subject?.toLowerCase().includes(searchLower)
    )
  })

  if (permLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="bg-white rounded-lg border border-slate-200 p-6 h-64 animate-pulse" />
      </div>
    )
  }

  if (!canRead('inbox')) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Inbox</h1>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view inbox.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Inbox</h1>
          <p className="text-slate-600 mt-1">Manage customer conversations</p>
        </div>
        {canWrite('inbox') && (
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${syncMutation.isPending ? 'animate-spin' : ''}`} />
            {syncMutation.isPending ? 'Syncing...' : 'Sync Gmail'}
          </button>
        )}
      </div>

      <div className="flex gap-2">
        {['all', 'active', 'pending', 'replied', 'closed'].map((status) => (
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

      <div className="flex gap-6 h-[calc(100vh-280px)]">
        <div className="w-1/3 bg-white rounded-lg border border-slate-200 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-20 bg-slate-200 rounded animate-pulse"></div>
                ))}
              </div>
            ) : filtered.length === 0 ? (
              <div className="p-8 text-center">
                <Mail className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <p className="text-slate-600">No conversations found</p>
              </div>
            ) : (
              <ConversationList
                conversations={filtered}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            )}
          </div>
        </div>

        <div className="flex-1 bg-white rounded-lg border border-slate-200">
          {selectedId ? (
            <MessageThread conversationId={selectedId} />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Mail className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">Select a conversation to view messages</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
