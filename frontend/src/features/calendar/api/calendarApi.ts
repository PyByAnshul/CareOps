import { apiClient } from '@/core/api/client'

export const calendarApi = {
  getSettings: () => apiClient.get('/api/calendar/settings').then(r => r.data),
  updateSettings: (data: any) => apiClient.put('/api/calendar/settings', data).then(r => r.data),
  sendInvite: (bookingId: number) => apiClient.post(`/api/calendar/send-invite/${bookingId}`).then(r => r.data),
}
