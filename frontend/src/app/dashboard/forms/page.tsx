'use client'

import { useQuery } from '@tanstack/react-query'
import { formsApi } from '@/features/forms/api/formsApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { Plus, FileText, Copy, Eye } from 'lucide-react'
import Link from 'next/link'

export default function FormsPage() {
  const { canRead, canWrite, isLoading: permLoading } = usePermissions()
  const { data: forms = [], isLoading } = useQuery({
    queryKey: ['forms'],
    queryFn: formsApi.list,
    enabled: canRead('forms'),
  })

  const copyLink = (token: string) => {
    const link = `${window.location.origin}/f/${token}`
    navigator.clipboard.writeText(link)
  }

  if (permLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="bg-white rounded-lg border border-slate-200 p-6 h-64 animate-pulse" />
      </div>
    )
  }

  if (!canRead('forms')) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Forms</h1>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view forms.
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Forms</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 bg-slate-200 rounded-lg animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Forms</h1>
          <p className="text-slate-600 mt-1">Manage custom forms and submissions</p>
        </div>
        {canWrite('forms') && (
          <Link
            href="/dashboard/forms/new"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Form
          </Link>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {forms.length === 0 ? (
          <div className="col-span-full bg-white rounded-lg border border-slate-200 p-12 text-center">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-600">No forms found</p>
          </div>
        ) : (
          forms.map((form: any) => (
            <Link
              key={form.id}
              href={`/dashboard/forms/${form.id}/edit`}
              className="bg-white rounded-lg border border-slate-200 p-6 hover:border-slate-300 hover:shadow-md transition-all cursor-pointer"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">{form.name}</h3>
                  <span className={`inline-block mt-1 px-2 py-1 rounded text-xs font-medium ${
                    form.form_type === 'booking' ? 'bg-blue-100 text-blue-700' :
                    form.form_type === 'inquiry' ? 'bg-purple-100 text-purple-700' :
                    'bg-orange-100 text-orange-700'
                  }`}>
                    {form.form_type === 'booking' ? 'Booking' : form.form_type === 'inquiry' ? 'Inquiry' : 'Quote'}
                  </span>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  form.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'
                }`}>
                  {form.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <p className="text-slate-600 text-sm mb-4">{form.description || 'No description'}</p>
              <div className="space-y-2">
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    copyLink(form.token)
                  }}
                  className="w-full flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg text-sm transition-colors"
                >
                  <Copy className="w-4 h-4" />
                  Copy Public Link
                </button>
                <Link
                  href={`/dashboard/forms/${form.id}`}
                  onClick={(e) => e.stopPropagation()}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  View Submissions
                </Link>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  )
}
