'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '@/features/alerts/api/alertsApi'
import { Alert } from '@/features/alerts/types'
import { AlertTriangle, X, ExternalLink } from 'lucide-react'
import { useState } from 'react'
import Link from 'next/link'

const severityColors = {
  critical: 'bg-red-100 border-red-300',
  high: 'bg-orange-100 border-orange-300',
  medium: 'bg-yellow-100 border-yellow-300',
  low: 'bg-blue-100 border-blue-300',
}

const severityBadgeColors = {
  critical: 'bg-red-600 text-white',
  high: 'bg-orange-600 text-white',
  medium: 'bg-yellow-600 text-white',
  low: 'bg-blue-600 text-white',
}

export default function AlertsPage() {
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState<string>('all')

  const { data: alerts = [], isLoading, error } = useQuery({
    queryKey: ['alerts'],
    queryFn: alertsApi.getAlerts,
  })

  const dismissMutation = useMutation({
    mutationFn: alertsApi.dismissAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter((a: Alert) => a.severity === filter)

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold text-slate-900">Alerts</h1>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-20 bg-slate-200 rounded-lg animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-red-700 bg-red-50 border border-red-200 rounded-lg p-4">
        Failed to load alerts
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Alerts</h1>
        <p className="text-slate-600 mt-1">System alerts and notifications</p>
      </div>

      <div className="flex gap-2">
        {['all', 'critical', 'high', 'medium', 'low'].map((sev) => (
          <button
            key={sev}
            onClick={() => setFilter(sev)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === sev
                ? 'bg-blue-600 text-white'
                : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {sev.charAt(0).toUpperCase() + sev.slice(1)}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="bg-white rounded-lg border border-slate-200 p-8 text-center">
            <AlertTriangle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-600">No alerts to display</p>
          </div>
        ) : (
          filteredAlerts.map((alert: Alert) => (
            <div
              key={alert.id}
              className={`border rounded-lg p-4 ${severityColors[alert.severity as keyof typeof severityColors]}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        severityBadgeColors[alert.severity as keyof typeof severityBadgeColors]
                      }`}
                    >
                      {alert.severity.toUpperCase()}
                    </span>
                    <h3 className="font-semibold text-slate-900">{alert.title}</h3>
                  </div>
                  <p className="text-slate-700 text-sm mb-3">{alert.message}</p>
                  <p className="text-xs text-slate-600">
                    {new Date(alert.created_at).toLocaleString()}
                  </p>
                </div>

                <div className="flex gap-2">
                  {alert.link && (
                    <a
                      href={alert.link}
                      className="p-2 hover:bg-white hover:bg-opacity-50 rounded transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  <button
                    onClick={() => dismissMutation.mutate(alert.id)}
                    className="p-2 hover:bg-white hover:bg-opacity-50 rounded transition-colors"
                    disabled={dismissMutation.isPending}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
