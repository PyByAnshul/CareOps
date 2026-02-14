'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/core/api/client'
import { Plus, Mail, Trash2, Edit, Save, X, Calendar, Users } from 'lucide-react'
import Link from 'next/link'

const INTEGRATION_TYPES = [
  {
    type: 'email',
    name: 'Email',
    icon: Mail,
    providers: [
      {
        value: 'smtp',
        label: 'SMTP',
        fields: [
          { name: 'host', label: 'SMTP Host', type: 'text', placeholder: 'smtp.gmail.com' },
          { name: 'port', label: 'Port', type: 'number', placeholder: '587' },
          { name: 'username', label: 'Username', type: 'text', placeholder: 'your@email.com' },
          { name: 'password', label: 'Password', type: 'password', placeholder: 'Your password' },
          { name: 'from_email', label: 'From Email', type: 'email', placeholder: 'noreply@yourcompany.com' },
        ]
      },
      {
        value: 'sendgrid',
        label: 'SendGrid',
        fields: [
          { name: 'api_key', label: 'API Key', type: 'password', placeholder: 'SG.xxxxx' },
          { name: 'from_email', label: 'From Email', type: 'email', placeholder: 'noreply@yourcompany.com' },
        ]
      },
      {
        value: 'gmail',
        label: 'Gmail',
        fields: [
          { name: 'client_id', label: 'Client ID', type: 'text', placeholder: 'Google OAuth Client ID' },
          { name: 'client_secret', label: 'Client Secret', type: 'password', placeholder: 'Google OAuth Client Secret' },
          { name: 'access_token', label: 'Access Token', type: 'password', placeholder: 'User Access Token' },
          { name: 'refresh_token', label: 'Refresh Token', type: 'password', placeholder: 'User Refresh Token' },
        ]
      }
    ]
  }
]

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    integration_type: 'email',
    provider: 'smtp',
    config: {} as any
  })

  const { data: integrations = [], isLoading } = useQuery({
    queryKey: ['integrations'],
    queryFn: async () => {
      const response = await apiClient.get('/api/integrations')
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/api/integrations', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
      setShowAddForm(false)
      setFormData({ integration_type: 'email', provider: 'smtp', config: {} })
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      const response = await apiClient.put(`/api/integrations/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
      setEditingId(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/integrations/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
    },
  })

  const selectedType = INTEGRATION_TYPES.find(t => t.type === formData.integration_type)
  const selectedProvider = selectedType?.providers.find(p => p.value === formData.provider)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
          <p className="text-slate-600 mt-1">Manage integrations and workspace settings</p>
        </div>
        <div className="flex gap-2">
          <Link
            href="/dashboard/settings/users"
            className="flex items-center gap-2 bg-slate-700 hover:bg-slate-800 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Users className="w-5 h-5" />
            Users
          </Link>
          <Link
            href="/dashboard/settings/calendar"
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Calendar className="w-5 h-5" />
            Calendar Settings
          </Link>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            {showAddForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
            {showAddForm ? 'Cancel' : 'Add Integration'}
          </button>
        </div>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Add Integration</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Integration Type</label>
                <select
                  value={formData.integration_type}
                  onChange={(e) => setFormData({ ...formData, integration_type: e.target.value, config: {} })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                >
                  {INTEGRATION_TYPES.map(type => (
                    <option key={type.type} value={type.type}>{type.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Provider</label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value, config: {} })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                >
                  {selectedType?.providers.map(provider => (
                    <option key={provider.value} value={provider.value}>{provider.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {selectedProvider?.fields.map(field => (
              <div key={field.name}>
                <label className="block text-sm font-medium text-slate-700 mb-1">{field.label}</label>
                <input
                  type={field.type}
                  value={formData.config[field.name] || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    config: { ...formData.config, [field.name]: e.target.value }
                  })}
                  placeholder={field.placeholder}
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                />
              </div>
            ))}

            <button
              type="submit"
              disabled={createMutation.isPending}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {createMutation.isPending ? 'Saving...' : 'Save Integration'}
            </button>
          </form>
        </div>
      )}

      {/* Integrations List */}
      <div className="bg-white rounded-lg border border-slate-200">
        <div className="p-6 border-b border-slate-200">
          <h2 className="text-xl font-semibold text-slate-900">Active Integrations</h2>
        </div>
        <div className="divide-y divide-slate-200">
          {isLoading ? (
            <div className="p-6 text-center text-slate-600">Loading...</div>
          ) : integrations.length === 0 ? (
            <div className="p-6 text-center text-slate-600">No integrations configured</div>
          ) : (
            integrations.map((integration: any) => (
              <div key={integration.id} className="p-6 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <Mail className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      {integration.integration_type.charAt(0).toUpperCase() + integration.integration_type.slice(1)} - {integration.provider.toUpperCase()}
                    </h3>
                    <p className="text-sm text-slate-600">
                      {integration.config.from_email || integration.config.username || 'Configured'}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    integration.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'
                  }`}>
                    {integration.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <button
                  onClick={() => {
                    if (confirm('Delete this integration?')) {
                      deleteMutation.mutate(integration.id)
                    }
                  }}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
