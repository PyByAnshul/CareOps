'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { googleFormsApi } from '@/features/google-forms/api/googleFormsApi'
import { useState } from 'react'
import { Plus, ExternalLink, Trash2, Copy, CheckCircle } from 'lucide-react'
import { FieldMappingEditor } from '@/features/google-forms/components/FieldMappingEditor'

export default function GoogleFormsPage() {
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    google_form_id: '',
    google_form_url: '',
    field_mappings: {} as Record<string, string>,
  })
  const [copiedSecret, setCopiedSecret] = useState<string | null>(null)

  const queryClient = useQueryClient()

  const { data: integrations = [], isLoading } = useQuery({
    queryKey: ['google-forms'],
    queryFn: googleFormsApi.list,
  })

  const createMutation = useMutation({
    mutationFn: googleFormsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['google-forms'] })
      resetForm()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: any) => googleFormsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['google-forms'] })
      resetForm()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: googleFormsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['google-forms'] })
    },
  })

  const resetForm = () => {
    setFormData({ name: '', google_form_id: '', google_form_url: '', field_mappings: {} })
    setShowForm(false)
    setEditingId(null)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleEdit = (integration: any) => {
    setFormData({
      name: integration.name,
      google_form_id: integration.google_form_id,
      google_form_url: integration.google_form_url,
      field_mappings: integration.field_mappings,
    })
    setEditingId(integration.id)
    setShowForm(true)
  }

  const copyWebhookUrl = (secret: string) => {
    // Backend URL for webhooks (not frontend URL)
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const url = `${backendUrl}/api/public/webhooks/google-forms/${secret}`
    navigator.clipboard.writeText(url)
    setCopiedSecret(secret)
    setTimeout(() => setCopiedSecret(null), 2000)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Google Forms Integration</h1>
          <p className="text-slate-600 mt-1">Connect Google Forms to create bookings automatically</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          New Integration
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">
            {editingId ? 'Edit Integration' : 'New Integration'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Integration Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Google Form ID</label>
              <input
                type="text"
                value={formData.google_form_id}
                onChange={(e) => setFormData({ ...formData, google_form_id: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g., 1FAIpQLSe..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Google Form URL</label>
              <input
                type="url"
                value={formData.google_form_url}
                onChange={(e) => setFormData({ ...formData, google_form_url: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="https://docs.google.com/forms/d/..."
                required
              />
            </div>

            <FieldMappingEditor
              mappings={formData.field_mappings}
              onChange={(mappings) => setFormData({ ...formData, field_mappings: mappings })}
            />

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
              >
                {editingId ? 'Update' : 'Create'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-24 bg-slate-200 rounded animate-pulse"></div>
            ))}
          </div>
        ) : integrations.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-slate-600">No Google Forms integrations yet</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-200">
            {integrations.map((integration: any) => (
              <div key={integration.id} className="p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-slate-900">{integration.name}</h3>
                    <a
                      href={integration.google_form_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1 mt-1"
                    >
                      View Form <ExternalLink className="w-3 h-3" />
                    </a>
                    
                    <div className="mt-3 space-y-2">
                      <div>
                        <p className="text-xs font-medium text-slate-500 mb-1">Webhook URL:</p>
                        <div className="flex gap-2 items-center">
                          <code className="text-xs bg-slate-100 px-2 py-1 rounded flex-1 overflow-x-auto">
                            {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/public/webhooks/google-forms/{integration.webhook_secret}
                          </code>
                          <button
                            onClick={() => copyWebhookUrl(integration.webhook_secret)}
                            className="p-2 text-slate-600 hover:bg-slate-100 rounded transition-colors"
                          >
                            {copiedSecret === integration.webhook_secret ? (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </button>
                        </div>
                      </div>

                      <div>
                        <p className="text-xs font-medium text-slate-500 mb-1">Field Mappings:</p>
                        <div className="text-xs text-slate-600 space-y-1">
                          {Object.entries(integration.field_mappings).map(([google, careops]) => (
                            <div key={google}>
                              <span className="font-medium">{google}</span> → {careops}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(integration)}
                      className="text-blue-600 hover:bg-blue-50 px-3 py-1 rounded transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(integration.id)}
                      className="text-red-600 hover:bg-red-50 p-2 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
