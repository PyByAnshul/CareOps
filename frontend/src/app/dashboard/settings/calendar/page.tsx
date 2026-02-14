'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { calendarApi } from '@/features/calendar/api/calendarApi'
import { useState, useEffect } from 'react'
import { Calendar, Mail, Save } from 'lucide-react'
import { BackButton } from '@/shared/components/BackButton'

export default function CalendarSettingsPage() {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    auto_send_invites: true,
    include_description: true,
    email_template: '',
  })

  const { data: settings, isLoading } = useQuery({
    queryKey: ['calendar-settings'],
    queryFn: calendarApi.getSettings,
  })

  useEffect(() => {
    if (settings) {
      setFormData({
        auto_send_invites: settings.auto_send_invites,
        include_description: settings.include_description,
        email_template: settings.email_template || '',
      })
    }
  }, [settings])

  const updateMutation = useMutation({
    mutationFn: calendarApi.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar-settings'] })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-slate-200 rounded w-1/3 animate-pulse"></div>
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
          <div className="h-12 bg-slate-200 rounded animate-pulse"></div>
          <div className="h-12 bg-slate-200 rounded animate-pulse"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3">
        <BackButton href="/dashboard/settings" label="Back to settings" />
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Calendar Settings</h1>
          <p className="text-slate-600 mt-1">Configure automatic calendar invites for bookings</p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="auto_send"
              checked={formData.auto_send_invites}
              onChange={(e) => setFormData({ ...formData, auto_send_invites: e.target.checked })}
              className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex-1">
              <label htmlFor="auto_send" className="block text-sm font-medium text-slate-900 cursor-pointer">
                Automatically send calendar invites
              </label>
              <p className="text-sm text-slate-600 mt-1">
                Send calendar invites (.ics files) via email when bookings are created
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="include_desc"
              checked={formData.include_description}
              onChange={(e) => setFormData({ ...formData, include_description: e.target.checked })}
              className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex-1">
              <label htmlFor="include_desc" className="block text-sm font-medium text-slate-900 cursor-pointer">
                Include booking details in description
              </label>
              <p className="text-sm text-slate-600 mt-1">
                Add service name, notes, and other details to the calendar event description
              </p>
            </div>
          </div>

          <div className="border-t border-slate-200 pt-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Mail className="w-5 h-5" />
              Email Template (Optional)
            </h3>
            <textarea
              value={formData.email_template}
              onChange={(e) => setFormData({ ...formData, email_template: e.target.value })}
              placeholder="Custom email message (leave empty for default template)"
              rows={6}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <p className="text-xs text-slate-500 mt-2">
              Available variables: {'{customer_name}'}, {'{service_name}'}, {'{booking_date}'}, {'{booking_time}'}
            </p>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
            </button>
            {updateMutation.isSuccess && (
              <span className="text-green-600 flex items-center gap-1 text-sm">
                ✓ Settings saved successfully
              </span>
            )}
          </div>
        </form>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex gap-3">
          <Calendar className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900">How it works</h4>
            <ul className="text-sm text-blue-800 mt-2 space-y-1 list-disc list-inside">
              <li>Calendar invites are sent automatically when bookings are created</li>
              <li>Customers receive an .ics file attachment they can add to any calendar app</li>
              <li>Works with Google Calendar, Outlook, Apple Calendar, and more</li>
              <li>Includes booking date, time, service details, and notes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
