'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { BackButton } from '@/shared/components/BackButton'
import { contactsApi } from '@/features/contacts/api/contactsApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import {
  Mail,
  Phone,
  Building,
  MapPin,
  Key,
  KeyRound,
  X,
} from 'lucide-react'

const typeLabels: Record<string, string> = {
  customer: 'Customer',
  supplier: 'Supplier',
  both: 'Customer & Supplier',
}

export default function ContactDetailPage() {
  const params = useParams()
  const contactId = params.id as string
  const queryClient = useQueryClient()
  const [modalOpen, setModalOpen] = useState(false)
  const [formEmail, setFormEmail] = useState('')
  const [formPassword, setFormPassword] = useState('')
  const [formError, setFormError] = useState('')

  const { canRead, canWrite } = usePermissions()
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
      setFormPassword('')
      setFormEmail('')
      setFormError('')
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to grant portal access')
    },
  })

  const openModal = () => {
    setFormEmail(contact?.email || '')
    setFormPassword('')
    setFormError('')
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setFormError('')
  }

  const hasContactEmail = !!contact?.email

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')
    if (!formPassword.trim()) {
      setFormError('Password is required')
      return
    }
    if (!hasContactEmail && !formEmail.trim()) {
      setFormError('Please enter both email and password for this contact')
      return
    }
    if (hasContactEmail) {
      grantMutation.mutate({ password: formPassword })
    } else {
      const email = formEmail.trim()
      if (!email) {
        setFormError('Please enter email and password')
        return
      }
      grantMutation.mutate({ email, password: formPassword })
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <BackButton href="/dashboard/contacts" label="Back to contacts" />
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-slate-200 rounded animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (!canRead('contacts')) {
    return (
      <div className="space-y-6">
        <BackButton href="/dashboard/contacts" label="Back to contacts" />
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view this contact.
        </div>
      </div>
    )
  }

  if (!contact) {
    return (
      <div className="space-y-6">
        <BackButton href="/dashboard/contacts" label="Back to contacts" />
        <p className="text-slate-600">Contact not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3">
        <BackButton href="/dashboard/contacts" label="Back to contacts" />
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">{contact.name}</h1>
            <p className="text-slate-600 mt-1">
              {typeLabels[contact.partner_type] || contact.partner_type}
              {contact.has_portal_access && (
                <span className="ml-2 inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-sm font-medium text-green-800">
                  <KeyRound className="w-3.5 h-3.5" />
                  Portal access
                </span>
              )}
            </p>
          </div>
          {!contact.has_portal_access && canWrite('contacts') && (
            <button
              type="button"
              onClick={openModal}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
            >
              <Key className="w-4 h-4" />
              Grant portal access
            </button>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {contact.email && (
              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-slate-600 mt-0.5" />
                <div>
                  <p className="text-sm text-slate-600">Email</p>
                  <p className="font-medium text-slate-900">{contact.email}</p>
                </div>
              </div>
            )}
            {contact.phone && (
              <div className="flex items-start gap-3">
                <Phone className="w-5 h-5 text-slate-600 mt-0.5" />
                <div>
                  <p className="text-sm text-slate-600">Phone</p>
                  <p className="font-medium text-slate-900">{contact.phone}</p>
                </div>
              </div>
            )}
            {contact.company && (
              <div className="flex items-start gap-3">
                <Building className="w-5 h-5 text-slate-600 mt-0.5" />
                <div>
                  <p className="text-sm text-slate-600">Company</p>
                  <p className="font-medium text-slate-900">{contact.company}</p>
                </div>
              </div>
            )}
            {contact.address && (
              <div className="flex items-start gap-3 md:col-span-2">
                <MapPin className="w-5 h-5 text-slate-600 mt-0.5" />
                <div>
                  <p className="text-sm text-slate-600">Address</p>
                  <p className="font-medium text-slate-900">{contact.address}</p>
                </div>
              </div>
            )}
          </div>
          {contact.notes && (
            <div className="border-t border-slate-200 pt-6">
              <p className="text-sm text-slate-600 mb-2">Notes</p>
              <p className="text-slate-900">{contact.notes}</p>
            </div>
          )}
        </div>
      </div>

      {/* Grant portal access modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-slate-900/50"
            aria-hidden
            onClick={closeModal}
          />
          <div className="relative w-full max-w-md rounded-lg bg-white shadow-xl border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <h2 className="text-lg font-semibold text-slate-900">
                Grant portal access
              </h2>
              <button
                type="button"
                onClick={closeModal}
                className="p-2 rounded-lg hover:bg-slate-100 text-slate-600"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {formError && (
                <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800">
                  {formError}
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
                    value={formEmail}
                    onChange={(e) => setFormEmail(e.target.value)}
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
                  value={formPassword}
                  onChange={(e) => setFormPassword(e.target.value)}
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
                  onClick={closeModal}
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

      {grantMutation.isSuccess && (
        <div className="rounded-lg bg-green-50 border border-green-200 p-4 text-green-800 text-sm">
          Portal access granted. This contact can now sign in with the email and password you set (staff user).
        </div>
      )}
    </div>
  )
}
