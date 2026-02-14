'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { webexApi } from '@/features/webex/api/webexApi'
import { Video, Plus, Trash2, ExternalLink, Calendar } from 'lucide-react'
import { useState } from 'react'
import Link from 'next/link'

export default function WebexMeetingsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const queryClient = useQueryClient()

  const { data: meetings = [], isLoading } = useQuery({
    queryKey: ['webex-meetings'],
    queryFn: webexApi.list,
  })

  const deleteMutation = useMutation({
    mutationFn: webexApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webex-meetings'] })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse"></div>
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-slate-200 rounded animate-pulse"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Webex Meetings</h1>
          <p className="text-slate-600 mt-1">Manage your Webex video meetings</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          New Meeting
        </button>
      </div>

      {showCreateForm && (
        <CreateMeetingForm onClose={() => setShowCreateForm(false)} />
      )}

      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Title</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Start Time</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Duration</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Booking</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {meetings.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center">
                  <Video className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-600">No meetings found</p>
                </td>
              </tr>
            ) : (
              meetings.map((meeting: any) => (
                <tr key={meeting.id} className="border-b border-slate-200 hover:bg-slate-50">
                  <td className="px-6 py-4">
                    <p className="font-medium text-slate-900">{meeting.title}</p>
                    {meeting.password && (
                      <p className="text-sm text-slate-600">Password: {meeting.password}</p>
                    )}
                  </td>
                  <td className="px-6 py-4 text-slate-900">
                    {new Date(meeting.start_time).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-slate-900">{meeting.duration} min</td>
                  <td className="px-6 py-4">
                    {meeting.booking_id ? (
                      <Link
                        href={`/dashboard/bookings/${meeting.booking_id}`}
                        className="text-blue-600 hover:underline"
                      >
                        Booking #{meeting.booking_id}
                      </Link>
                    ) : (
                      <span className="text-slate-500">Custom</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <a
                        href={meeting.meeting_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                        title="Join Meeting"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                      <button
                        onClick={() => {
                          if (confirm('Delete this meeting?')) {
                            deleteMutation.mutate(meeting.id)
                          }
                        }}
                        className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Delete Meeting"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function CreateMeetingForm({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    title: '',
    start_time: '',
    duration: 60,
  })

  const createMutation = useMutation({
    mutationFn: webexApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webex-meetings'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-slate-900">Create New Meeting</h2>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
          ×
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Meeting Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              <Calendar className="w-4 h-4 inline mr-1" />
              Start Time
            </label>
            <input
              type="datetime-local"
              value={formData.start_time}
              onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Duration (minutes)
            </label>
            <input
              type="number"
              value={formData.duration}
              onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              min="15"
              step="15"
              required
            />
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <Video className="w-4 h-4" />
            {createMutation.isPending ? 'Creating...' : 'Create Meeting'}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="bg-slate-200 hover:bg-slate-300 text-slate-900 px-4 py-2 rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>

        {createMutation.isError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-800 text-sm">
            {(createMutation.error as any)?.response?.data?.detail || 'Failed to create meeting. Please check your Webex integration settings.'}
          </div>
        )}
      </form>
    </div>
  )
}
