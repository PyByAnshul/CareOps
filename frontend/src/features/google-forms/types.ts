export interface GoogleFormIntegration {
  id: number
  workspace_id: number
  name: string
  google_form_id: string
  google_form_url: string
  webhook_secret: string
  field_mappings: Record<string, string>
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface GoogleFormSubmission {
  id: number
  integration_id: number
  booking_id: number | null
  raw_data: Record<string, any>
  mapped_data: Record<string, any>
  status: 'pending' | 'processed' | 'failed'
  error_message: string | null
  created_at: string
}

export interface CreateGoogleFormIntegration {
  name: string
  google_form_id: string
  google_form_url: string
  field_mappings: Record<string, string>
}
