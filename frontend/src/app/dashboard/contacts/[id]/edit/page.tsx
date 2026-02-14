'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, Trash2, User, Mail, Phone, Building, Key, X } from 'lucide-react'
import { contactsApi } from '@/features/contacts/api/contactsApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { BackButton } from '@/shared/components/BackButton'

export default function EditContactPage() {
  const router = useRouter()
  const params = useParams()
  const contactId = params.id as string
  const queryClient = useQueryClient()
  const [modalOpen, setModalOpen] = useState(false)
  const [grantEmail, setGrantEmail] = useState('')
  const [grantPassword, setGrantPassword] = useState('')
  const [grantError, setGrantError] = useState('')
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    address: '',
    partner_type: 'customer',
    has_portal_access: false,
    notes: ''
  })
  const [isSaving, setIsSaving] = useState(false)

  const { canRead, canWrite, canDelete } = usePermissions()
  const { data: contact, isLoading } = useQuery({
    queryKey: ['contact', contactId],
    queryFn: () => contactsApi.get(contactId),
    enabled: canRead('contacts'),
  })

  const grantMutation = useMutation({
    mutationFn: (data: { email?: string; password: string }) =>
      contactsApi.grantPortalAccess(contactId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contact', contactId] })
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
      setModalOpen(false)
      setGrantPassword('')
      setGrantEmail('')
      setGrantError('')
      setFormData((prev) => ({ ...prev, has_portal_access: true }))
    },
    onError: (err: any) => {
      setGrantError(err.response?.data?.detail || 'Failed to grant portal access')
    },
  })

  const openGrantModal = () => {
    setGrantEmail(contact?.email || formData.email || '')
    setGrantPassword('')
    setGrantError('')
    setModalOpen(true)
  }

  const hasContactEmail = !!contact?.email

  const handleGrantSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setGrantError('')
    if (!grantPassword.trim()) {
      setGrantError('Password is required')
      return
    }
    if (!hasContactEmail && !grantEmail.trim()) {
      setGrantError('Please enter both email and password for this contact')
      return
    }
    if (hasContactEmail) {
      grantMutation.mutate({ password: grantPassword })
    } else {
      grantMutation.mutate({ email: grantEmail.trim(), password: grantPassword })
    }
  }

  useEffect(() => {
    if (contact) {
      setFormData({
        name: contact.name || '',
        email: contact.email || '',
        phone: contact.phone || '',
        company: contact.company || '',
        address: contact.address || '',
        partner_type: contact.partner_type || 'customer',
        has_portal_access: contact.has_portal_access || false,
        notes: contact.notes || ''
      })
    }
  }, [contact])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await contactsApi.update(contactId, formData)
      router.push('/dashboard/contacts')
    } catch (error) {
      console.error('Failed to update contact:', error)
      alert('Failed to update contact')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this contact?')) {
      try {
        await contactsApi.delete(contactId)
        router.push('/dashboard/contacts')
      } catch (error) {
        console.error('Failed to delete contact:', error)
        alert('Failed to delete contact')
      }
    }
  }

  if (isLoading) {
    return (
      <div className="h-full bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!canRead('contacts')) {
    return (
      <div className="h-full bg-slate-50 p-6">
        <BackButton href="/dashboard/contacts" label="Back to contacts" />
        <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view or edit contacts.
        </div>
      </div>
    )
  }

  if (!contact) {
    return (
      <div className="h-full bg-slate-50 flex items-center justify-center">
        <p className="text-slate-600">Contact not found</p>
      </div>
    )
  }

  return (
    <div className="h-full bg-slate-50">
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <BackButton href="/dashboard/contacts" label="Back to contacts" />
            <div>
              <h1 className="text-xl font-semibold text-slate-900">Edit Contact</h1>
              <p className="text-sm text-slate-600">Modify contact information</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {!contact.has_portal_access && canWrite('contacts') && (
              <button
                type="button"
                onClick={openGrantModal}
                className="flex items-center px-3 py-2 text-sm border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50"
              >
                <Key className="w-4 h-4 mr-2" />
                Grant portal access
              </button>
            )}
            {canDelete('contacts') && (
              <button onClick={handleDelete} className="flex items-center px-3 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </button>
            )}
            {canWrite('contacts') && (
            <button onClick={handleSave} disabled={isSaving} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
            )}
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <User className="w-4 h-4 inline mr-2" />
                  Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Phone className="w-4 h-4 inline mr-2" />
                  Phone
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Building className="w-4 h-4 inline mr-2" />
                  Company
                </label>
                <input
                  type="text"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Partner Type</label>
                <select
                  value={formData.partner_type}
                  onChange={(e) => setFormData({ ...formData, partner_type: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="customer">Customer</option>
                  <option value="supplier">Supplier</option>
                  <option value="both">Both</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="portal_access"
                  checked={formData.has_portal_access}
                  onChange={(e) => setFormData({ ...formData, has_portal_access: e.target.checked })}
                />
                <label htmlFor="portal_access" className="text-sm font-medium text-slate-700">
                  Has Portal Access
                </label>
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">Address</label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Grant portal access modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-slate-900/50"
            aria-hidden
            onClick={() => setModalOpen(false)}
          />
          <div className="relative w-full max-w-md rounded-lg bg-white shadow-xl border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <h2 className="text-lg font-semibold text-slate-900">
                Grant portal access
              </h2>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="p-2 rounded-lg hover:bg-slate-100 text-slate-600"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleGrantSubmit} className="p-6 space-y-4">
              {grantError && (
                <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800">
                  {grantError}
                </div>
              )}
              {hasContactEmail ? (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Email (from contact)
                  </label>
                  <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700">
                    <Mail className="w-4 h-4 text-slate-500" />
                    <span>{contact.email}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    This user will sign in with this email. Set a password below.
                  </p>
                </div>
              ) : (
                <div>
                  <label htmlFor="grant-email" className="block text-sm font-medium text-slate-700 mb-1">
                    Email
                  </label>
                  <input
                    id="grant-email"
                    type="email"
                    value={grantEmail}
                    onChange={(e) => setGrantEmail(e.target.value)}
                    placeholder="user@example.com"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                    autoComplete="email"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    This contact has no email. Enter email and password to create a staff login.
                  </p>
                </div>
              )}
              <div>
                <label htmlFor="grant-password" className="block text-sm font-medium text-slate-700 mb-1">
                  Password
                </label>
                <input
                  id="grant-password"
                  type="password"
                  value={grantPassword}
                  onChange={(e) => setGrantPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                  minLength={6}
                  autoComplete="new-password"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Minimum 6 characters. They will use this to sign in to the portal (staff).
                </p>
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={grantMutation.isPending}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {grantMutation.isPending ? 'Creating…' : 'Confirm'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}