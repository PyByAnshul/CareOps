import { apiClient } from '@/core/api/client'

export const webexApi = {
  list: () => apiClient.get('/api/webex/meetings').then(r => r.data),
  create: (data: any) => apiClient.post('/api/webex/meetings', data).then(r => r.data),
  getByBooking: (bookingId: number) => apiClient.get(`/api/webex/meetings/booking/${bookingId}`).then(r => r.data),
  delete: (id: number) => apiClient.delete(`/api/webex/meetings/${id}`),
}
