import { apiClient } from '@/core/api/client'

export const alertsApi = {
  getAlerts: (params?: any) => apiClient.get('/api/alerts', { params }).then(r => r.data),
  dismissAlert: (id: string) => apiClient.post(`/api/alerts/${id}/dismiss`).then(r => r.data),
}
