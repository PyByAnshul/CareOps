'use client'

import { useQuery } from '@tanstack/react-query'
import { contactsApi } from '@/features/contacts/api/contactsApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { Plus, Eye, Users } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

const typeColors = {
  customer: 'bg-blue-100 text-blue-700',
  supplier: 'bg-green-100 text-green-700',
  both: 'bg-purple-100 text-purple-700',
}

export default function ContactsPage() {
  const [typeFilter, setTypeFilter] = useState('all')
  const [accessFilter, setAccessFilter] = useState('all')
  const [search, setSearch] = useState('')
  const { canRead, canWrite, isLoading: permLoading } = usePermissions()

  const { data: contacts = [], isLoading } = useQuery({
    queryKey: ['contacts'],
    queryFn: contactsApi.list,
    enabled: canRead('contacts'),
  })

  const filtered = contacts.filter((c: any) => {
    const matchType = typeFilter === 'all' || c.partner_type === typeFilter
    const matchAccess = accessFilter === 'all' || 
      (accessFilter === 'with' && c.has_portal_access) ||
      (accessFilter === 'without' && !c.has_portal_access)
    const matchSearch = !search || 
      c.name?.toLowerCase().includes(search.toLowerCase()) ||
      c.email?.toLowerCase().includes(search.toLowerCase()) ||
      c.company?.toLowerCase().includes(search.toLowerCase())
    return matchType && matchAccess && matchSearch
  })

  if (permLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="bg-white rounded-lg border border-slate-200 p-6 h-64 animate-pulse" />
      </div>
    )
  }

  if (!canRead('contacts')) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Contacts</h1>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view contacts.
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Contacts</h1>
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-slate-200 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Contacts</h1>
          <p className="text-slate-600 mt-1">Manage customers and suppliers</p>
        </div>
        {canWrite('contacts') && (
          <Link
            href="/dashboard/contacts/new"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Contact
          </Link>
        )}
      </div>

      <div className="flex gap-4 items-center">
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        >
          <option value="all">All Types</option>
          <option value="customer">Customer</option>
          <option value="supplier">Supplier</option>
          <option value="both">Both</option>
        </select>

        <select
          value={accessFilter}
          onChange={(e) => setAccessFilter(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        >
          <option value="all">All Access</option>
          <option value="with">With Portal Access</option>
          <option value="without">Without Portal Access</option>
        </select>

        <input
          type="text"
          placeholder="Search contacts..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>

      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Name</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Email</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Phone</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Company</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Type</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Portal Access</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center">
                  <Users className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-600">No contacts found</p>
                </td>
              </tr>
            ) : (
              filtered.map((contact: any) => (
                <tr key={contact.id} className="border-b border-slate-200 hover:bg-slate-50 transition-colors cursor-pointer"
                    onClick={() => window.location.href = `/dashboard/contacts/${contact.id}/edit`}>
                  <td className="px-6 py-4 font-medium text-slate-900">{contact.name}</td>
                  <td className="px-6 py-4 text-slate-600">{contact.email || '-'}</td>
                  <td className="px-6 py-4 text-slate-600">{contact.phone || '-'}</td>
                  <td className="px-6 py-4 text-slate-600">{contact.company || '-'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${typeColors[contact.partner_type as keyof typeof typeColors]}`}>
                      {contact.partner_type}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      contact.has_portal_access ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {contact.has_portal_access ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <Link
                      href={`/dashboard/contacts/${contact.id}`}
                      onClick={(e) => e.stopPropagation()}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors inline-block"
                    >
                      <Eye className="w-4 h-4" />
                    </Link>
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
