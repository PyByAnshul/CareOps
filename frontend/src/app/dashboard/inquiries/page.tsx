'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { formsApi } from '@/features/forms/api/formsApi'
import { Mail, Clock, CheckCircle, XCircle, User } from 'lucide-react'
import { useState } from 'react'

const statusColors = {
  new: 'bg-blue-100 text-blue-700',
  contacted: 'bg-yellow-100 text-yellow-700',
  converted: 'bg-green-100 text-green-700',
  closed: 'bg-slate-100 text-slate-700',
}

const statusLabels = {
  new: 'New',
  contacted: 'Contacted',
  converted: 'Converted',
  closed: 'Closed',
}

export default function InquiriesPage() {
  const [filter, setFilter] = useState<string>('')
  const queryClient = useQueryClient()

  const { data: inquiries = [], isLoading } = useQuery({
    queryKey: ['inquiries', filter],
    queryFn: () => formsApi.listInquiries(filter || undefined),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      formsApi.updateInquiry(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inquiries'] })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Inquiries</h1>
        <div className="grid gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-200 rounded-lg animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Inquiries</h1>
        <p className="text-slate-600 mt-1">Manage customer inquiries and quote requests</p>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setFilter('')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === '' ? 'bg-blue-600 text-white' : 'bg-white border border-slate-300 text-slate-700'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('new')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'new' ? 'bg-blue-600 text-white' : 'bg-white border border-slate-300 text-slate-700'
          }`}
        >
          New
        </button>
        <button
          onClick={() => setFilter('contacted')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'contacted' ? 'bg-blue-600 text-white' : 'bg-white border border-slate-300 text-slate-700'
          }`}
        >
          Contacted
        </button>
      </div>

      <div className="grid gap-4">
        {inquiries.length === 0 ? (
          <div className="bg-white rounded-lg border border-slate-200 p-12 text-center">
            <Mail className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-600">No inquiries found</p>
          </div>
        ) : (
          inquiries.map((inquiry: any) => (
            <div
              key={inquiry.id}
              className="bg-white rounded-lg border border-slate-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-slate-900">{inquiry.customer_name}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[inquiry.status as keyof typeof statusColors]}`}>
                      {statusLabels[inquiry.status as keyof typeof statusLabels]}
                    </span>
                    <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-700">
                      {inquiry.inquiry_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-slate-600">
                    <span className="flex items-center gap-1">
                      <Mail className="w-4 h-4" />
                      {inquiry.customer_email}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {new Date(inquiry.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {inquiry.status === 'new' && (
                    <button
                      onClick={() => updateMutation.mutate({ id: inquiry.id, status: 'contacted' })}
                      className="px-3 py-1 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
                    >
                      Mark Contacted
                    </button>
                  )}
                  {inquiry.status === 'contacted' && (
                    <button
                      onClick={() => updateMutation.mutate({ id: inquiry.id, status: 'converted' })}
                      className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                    >
                      Mark Converted
                    </button>
                  )}
                  <button
                    onClick={() => updateMutation.mutate({ id: inquiry.id, status: 'closed' })}
                    className="px-3 py-1 text-sm bg-slate-600 text-white rounded hover:bg-slate-700 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
              {inquiry.subject && (
                <div className="mb-2">
                  <span className="text-sm font-medium text-slate-700">Subject: </span>
                  <span className="text-sm text-slate-600">{inquiry.subject}</span>
                </div>
              )}
              {inquiry.message && (
                <div className="text-sm text-slate-600 bg-slate-50 p-3 rounded">
                  {inquiry.message}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
