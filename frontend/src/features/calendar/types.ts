export interface CalendarSettings {
  id: number
  workspace_id: number
  auto_send_invites: boolean
  include_description: boolean
  email_template: string | null
  created_at: string
  updated_at: string
}

export interface UpdateCalendarSettings {
  auto_send_invites?: boolean
  include_description?: boolean
  email_template?: string
}
