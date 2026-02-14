export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low'
export type AlertType = 'automation_failed' | 'booking_conflict' | 'stock_low' | 'system'

export interface Alert {
  id: number
  type: AlertType
  severity: AlertSeverity
  title: string
  message: string
  link?: string
  is_dismissed: boolean
  created_at: string
}
