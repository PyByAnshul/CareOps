'use client'

import { X, Plus } from 'lucide-react'
import { useState } from 'react'

interface FieldMappingEditorProps {
  mappings: Record<string, string>
  onChange: (mappings: Record<string, string>) => void
}

const CAREOPS_FIELDS = [
  { value: 'customer_name', label: 'Customer Name' },
  { value: 'customer_email', label: 'Customer Email' },
  { value: 'service_name', label: 'Service Name' },
  { value: 'booking_date', label: 'Booking Date' },
  { value: 'booking_time', label: 'Booking Time' },
  { value: 'notes', label: 'Notes' },
]

export function FieldMappingEditor({ mappings, onChange }: FieldMappingEditorProps) {
  const [entries, setEntries] = useState<Array<[string, string]>>(
    Object.entries(mappings).length > 0 ? Object.entries(mappings) : [['', '']]
  )

  const updateMappings = (newEntries: Array<[string, string]>) => {
    setEntries(newEntries)
    const obj = Object.fromEntries(newEntries.filter(([k, v]) => k && v))
    onChange(obj)
  }

  const addMapping = () => {
    updateMappings([...entries, ['', '']])
  }

  const removeMapping = (index: number) => {
    updateMappings(entries.filter((_, i) => i !== index))
  }

  const updateEntry = (index: number, key: string, value: string) => {
    const newEntries = [...entries]
    newEntries[index] = [key, value]
    updateMappings(newEntries)
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <label className="block text-sm font-medium text-slate-700">Field Mappings</label>
        <button
          type="button"
          onClick={addMapping}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          <Plus className="w-4 h-4" />
          Add Mapping
        </button>
      </div>

      <div className="space-y-2">
        {entries.map(([googleField, careopsField], index) => (
          <div key={index} className="flex gap-2 items-center">
            <input
              type="text"
              placeholder="Google Form Question"
              value={googleField}
              onChange={(e) => updateEntry(index, e.target.value, careopsField)}
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <span className="text-slate-400">→</span>
            <select
              value={careopsField}
              onChange={(e) => updateEntry(index, googleField, e.target.value)}
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option value="">Select CareOps Field</option>
              {CAREOPS_FIELDS.map((field) => (
                <option key={field.value} value={field.value}>
                  {field.label}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => removeMapping(index)}
              className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>

      <p className="text-xs text-slate-500">
        Map Google Form questions to CareOps booking fields. The question title must match exactly.
      </p>
    </div>
  )
}
