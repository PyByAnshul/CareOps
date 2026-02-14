'use client'

import { useQuery, useMutation } from '@tanstack/react-query'
import { formsApi } from '@/features/forms/api/formsApi'
import { servicesApi } from '@/features/services/api/servicesApi'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { CheckCircle } from 'lucide-react'

export default function PublicFormPage() {
  const params = useParams()
  const [answers, setAnswers] = useState<any>({})
  const [contactEmail, setContactEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const { data: form, isLoading } = useQuery({
    queryKey: ['public-form', params.token],
    queryFn: () => formsApi.getPublic(params.token as string),
  })

  const { data: services = [] } = useQuery({
    queryKey: ['services'],
    queryFn: servicesApi.list,
    enabled: !!form,
  })

  const mutation = useMutation({
    mutationFn: (data: any) => formsApi.submitPublic(params.token as string, data),
    onSuccess: () => setSubmitted(true),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-600">Loading form...</div>
      </div>
    )
  }

  if (!form) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-600">Form not found</div>
      </div>
    )
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="bg-white rounded-lg border border-slate-200 p-8 max-w-md text-center">
          <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Thank You!</h2>
          <p className="text-slate-600">Your submission has been received.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg border border-slate-200 p-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">{form.form_name}</h1>
          
          <form onSubmit={(e) => {
            e.preventDefault()
            if (!contactEmail.trim()) {
              alert('Please enter your email address')
              return
            }
            mutation.mutate({ 
              contact_email: contactEmail,
              answers 
            })
          }} className="space-y-6">
            {/* Contact Email Field */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Email Address <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                value={contactEmail}
                onChange={(e) => setContactEmail(e.target.value)}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Enter your email address"
              />
            </div>

            {/* Form Fields */}
            {form.schema?.fields?.map((field: any, idx: number) => (
              <div key={idx}>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                {field.type === 'textarea' ? (
                  <textarea
                    value={answers[field.label] || ''}
                    onChange={(e) => setAnswers({ ...answers, [field.label]: e.target.value })}
                    required={field.required}
                    placeholder={field.placeholder}
                    rows={4}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                ) : field.type === 'select' ? (
                  <select
                    value={answers[field.label] || ''}
                    onChange={(e) => setAnswers({ ...answers, [field.label]: e.target.value })}
                    required={field.required}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    <option value="">{field.placeholder || 'Select an option'}</option>
                    {field.label === 'service_id' ? (
                      services.map((service: any) => (
                        <option key={service.id} value={service.id}>{service.name}</option>
                      ))
                    ) : (
                      field.options?.map((option: string, optIdx: number) => (
                        <option key={optIdx} value={option}>{option}</option>
                      ))
                    )}
                  </select>
                ) : field.type === 'checkbox' ? (
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`field_${idx}`}
                      checked={answers[field.label] || false}
                      onChange={(e) => setAnswers({ ...answers, [field.label]: e.target.checked })}
                      required={field.required}
                    />
                    <label htmlFor={`field_${idx}`} className="text-sm text-slate-700">
                      {field.label}
                    </label>
                  </div>
                ) : (
                  <input
                    type={field.type}
                    value={answers[field.label] || ''}
                    onChange={(e) => setAnswers({ ...answers, [field.label]: e.target.value })}
                    required={field.required}
                    placeholder={field.placeholder}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                )}
              </div>
            ))}

            <button
              type="submit"
              disabled={mutation.isPending}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white px-6 py-3 rounded-lg transition-colors"
            >
              {mutation.isPending ? 'Submitting...' : 'Submit'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
