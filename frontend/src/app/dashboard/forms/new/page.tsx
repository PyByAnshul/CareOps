'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Plus, 
  Save, 
  X, 
  GripVertical, 
  Type, 
  Mail, 
  Phone, 
  Calendar, 
  CheckSquare, 
  List, 
  FileText,
  Eye
} from 'lucide-react'
import { formsApi } from '@/features/forms/api/formsApi'
import { BackButton } from '@/shared/components/BackButton'

interface FormField {
  id: string
  type: 'text' | 'email' | 'phone' | 'textarea' | 'select' | 'checkbox' | 'date'
  label: string
  placeholder?: string
  required: boolean
  options?: string[]
}

const fieldTypes = [
  { value: 'text', label: 'Text Input', icon: Type },
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'phone', label: 'Phone', icon: Phone },
  { value: 'textarea', label: 'Text Area', icon: FileText },
  { value: 'select', label: 'Dropdown', icon: List },
  { value: 'checkbox', label: 'Checkbox', icon: CheckSquare },
  { value: 'date', label: 'Date', icon: Calendar },
]

export default function NewFormPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: '',
    form_type: 'booking' as 'booking' | 'inquiry' | 'quote',
    description: '',
    is_active: true
  })
  const [fields, setFields] = useState<FormField[]>([])
  const [selectedField, setSelectedField] = useState<FormField | null>(null)
  const [isPreview, setIsPreview] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Required booking fields that are always present
  const getRequiredBookingFields = (): FormField[] => [
    {
      id: 'customer_name',
      type: 'text',
      label: 'Customer Name',
      placeholder: 'Enter your full name',
      required: true
    },
    {
      id: 'service_id',
      type: 'select',
      label: 'Service',
      placeholder: 'Select a service',
      required: true,
      options: ['General Consultation', 'Physical Therapy', 'Blood Test']
    },
    {
      id: 'booking_date',
      type: 'date',
      label: 'Preferred Date',
      required: true
    },
    {
      id: 'booking_time',
      type: 'text',
      label: 'Preferred Time',
      placeholder: 'HH:MM (e.g., 14:30)',
      required: true
    },
    {
      id: 'notes',
      type: 'textarea',
      label: 'Additional Notes',
      placeholder: 'Any special requirements or notes',
      required: false
    }
  ]

  // Get all fields including required ones for booking forms
  const getAllFields = () => {
    if (formData.form_type === 'booking') {
      return [...getRequiredBookingFields(), ...fields]
    }
    return fields
  }

  const addField = (type: FormField['type']) => {
    const newField: FormField = {
      id: `field_${Date.now()}`,
      type,
      label: `New ${type} field`,
      placeholder: '',
      required: false,
      options: type === 'select' ? ['Option 1', 'Option 2'] : undefined
    }
    setFields([...fields, newField])
    setSelectedField(newField)
  }

  const updateField = (id: string, updates: Partial<FormField>) => {
    setFields(fields.map(field => 
      field.id === id ? { ...field, ...updates } : field
    ))
    if (selectedField?.id === id) {
      setSelectedField({ ...selectedField, ...updates })
    }
  }

  const removeField = (id: string) => {
    setFields(fields.filter(field => field.id !== id))
    if (selectedField?.id === id) {
      setSelectedField(null)
    }
  }

  const handleSave = async () => {
    if (!formData.name.trim()) {
      alert('Please enter a form name')
      return
    }

    setIsSaving(true)
    try {
      const allFields = getAllFields()
      await formsApi.create({
        name: formData.name,
        form_type: formData.form_type,
        schema: {
          fields: allFields.map(({ id, ...field }) => field)
        }
      })
      router.push('/dashboard/forms')
    } catch (error) {
      console.error('Failed to save form:', error)
      alert('Failed to save form')
    } finally {
      setIsSaving(false)
    }
  }

  const renderFieldPreview = (field: FormField) => {
    const commonProps = {
      placeholder: field.placeholder,
      required: field.required,
      className: "w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    }

    switch (field.type) {
      case 'text':
        return <input type="text" {...commonProps} />
      case 'email':
        return <input type="email" {...commonProps} />
      case 'phone':
        return <input type="tel" {...commonProps} />
      case 'textarea':
        return <textarea {...commonProps} rows={3} />
      case 'select':
        return (
          <select {...commonProps}>
            <option value="">{field.placeholder || 'Select an option'}</option>
            {field.options?.map((option, index) => (
              <option key={index} value={option}>{option}</option>
            ))}
          </select>
        )
      case 'checkbox':
        return (
          <div className="flex items-center space-x-2">
            <input type="checkbox" id={field.id} />
            <label htmlFor={field.id}>{field.label}</label>
          </div>
        )
      case 'date':
        return <input type="date" {...commonProps} />
      default:
        return <input type="text" {...commonProps} />
    }
  }

  return (
    <div className="h-full bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <BackButton href="/dashboard/forms" label="Back to forms" />
            <div>
              <h1 className="text-xl font-semibold text-slate-900">New Form</h1>
              <p className="text-sm text-slate-600">Create a new form to collect data</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsPreview(!isPreview)}
              className="flex items-center px-3 py-2 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <Eye className="w-4 h-4 mr-2" />
              {isPreview ? 'Edit' : 'Preview'}
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      </div>

      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Panel - Form Builder */}
        {!isPreview && (
          <div className="w-80 bg-white border-r border-slate-200 flex flex-col">
            {/* Form Settings */}
            <div className="p-4 border-b border-slate-200">
              <h3 className="font-medium text-slate-900 mb-3">Form Settings</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Form Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Enter form name"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Form Type</label>
                  <select
                    value={formData.form_type}
                    onChange={(e) => setFormData({ ...formData, form_type: e.target.value as any })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="booking">Booking Request</option>
                    <option value="inquiry">General Inquiry</option>
                    <option value="quote">Quote Request</option>
                  </select>
                  <p className="text-xs text-slate-500 mt-1">
                    {formData.form_type === 'booking' && 'Creates a booking automatically'}
                    {formData.form_type === 'inquiry' && 'Creates an inquiry for follow-up'}
                    {formData.form_type === 'quote' && 'Creates a quote request'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Enter form description"
                    rows={2}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Field Types */}
            <div className="p-4 border-b border-slate-200">
              <h3 className="font-medium text-slate-900 mb-3">Add Fields</h3>
              {formData.form_type === 'booking' && (
                <p className="text-xs text-blue-600 mb-3 p-2 bg-blue-50 rounded">
                  ℹ️ Required booking fields are auto-added. Add custom fields below.
                </p>
              )}
              <div className="grid grid-cols-2 gap-2">
                {fieldTypes.map((fieldType) => {
                  const Icon = fieldType.icon
                  return (
                    <button
                      key={fieldType.value}
                      onClick={() => addField(fieldType.value as FormField['type'])}
                      className="flex items-center justify-start h-auto p-2 text-xs border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      <span>{fieldType.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Field Properties */}
            {selectedField && (
              <div className="p-4 flex-1 overflow-y-auto">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-slate-900">Field Properties</h3>
                  <button
                    onClick={() => removeField(selectedField.id)}
                    className="p-1 hover:bg-slate-100 rounded transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Field Label</label>
                    <input
                      type="text"
                      value={selectedField.label}
                      onChange={(e) => updateField(selectedField.id, { label: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Placeholder</label>
                    <input
                      type="text"
                      value={selectedField.placeholder || ''}
                      onChange={(e) => updateField(selectedField.id, { placeholder: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="required"
                      checked={selectedField.required}
                      onChange={(e) => updateField(selectedField.id, { required: e.target.checked })}
                    />
                    <label htmlFor="required" className="text-sm font-medium text-slate-700">Required field</label>
                  </div>
                  {selectedField.type === 'select' && (
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Options</label>
                      <div className="space-y-2">
                        {selectedField.options?.map((option, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <input
                              type="text"
                              value={option}
                              onChange={(e) => {
                                const newOptions = [...(selectedField.options || [])]
                                newOptions[index] = e.target.value
                                updateField(selectedField.id, { options: newOptions })
                              }}
                              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <button
                              onClick={() => {
                                const newOptions = selectedField.options?.filter((_, i) => i !== index)
                                updateField(selectedField.id, { options: newOptions })
                              }}
                              className="p-2 hover:bg-slate-100 rounded transition-colors"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                        <button
                          onClick={() => {
                            const newOptions = [...(selectedField.options || []), `Option ${(selectedField.options?.length || 0) + 1}`]
                            updateField(selectedField.id, { options: newOptions })
                          }}
                          className="flex items-center px-3 py-2 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Add Option
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Main Content - Form Preview */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
              <div className="p-6 border-b border-slate-200">
                <h2 className="text-lg font-semibold text-slate-900">{formData.name || 'Untitled Form'}</h2>
                {formData.description && (
                  <p className="text-sm text-slate-600 mt-1">{formData.description}</p>
                )}
              </div>
              <div className="p-6 space-y-6">
                {getAllFields().length === 0 ? (
                  <div className="text-center py-12 text-slate-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                    <p>No fields added yet</p>
                    <p className="text-sm">Add fields from the left panel to build your form</p>
                  </div>
                ) : (
                  getAllFields().map((field, index) => {
                    const isRequired = formData.form_type === 'booking' && 
                      ['customer_name', 'service_id', 'booking_date', 'booking_time'].includes(field.id)
                    
                    return (
                      <div
                        key={field.id}
                        className={`group relative p-4 rounded-lg border transition-colors ${
                          isRequired ? 'border-blue-300 bg-blue-50' : 'border-slate-200'
                        } ${
                          selectedField?.id === field.id && !isPreview
                            ? 'border-blue-500 bg-blue-50'
                            : 'hover:border-slate-300'
                        } ${
                          isRequired && !isPreview ? 'cursor-default' : 'cursor-pointer'
                        }`}
                        onClick={() => !isPreview && !isRequired && setSelectedField(field)}
                      >
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <label className="text-sm font-medium text-slate-700">
                              {field.label}
                              {field.required && <span className="text-red-500 ml-1">*</span>}
                              {isRequired && <span className="ml-2 text-xs px-2 py-0.5 bg-blue-600 text-white rounded">Required</span>}
                            </label>
                            {!isPreview && !isRequired && (
                              <span className="text-xs px-2 py-1 bg-slate-200 text-slate-700 rounded">
                                {fieldTypes.find(t => t.value === field.type)?.label}
                              </span>
                            )}
                          </div>
                          {field.type === 'checkbox' ? (
                            renderFieldPreview(field)
                          ) : (
                            <div>
                              {renderFieldPreview(field)}
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })
                )}
                
                {getAllFields().length > 0 && (
                  <div className="pt-4">
                    <button className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      Submit Form
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}