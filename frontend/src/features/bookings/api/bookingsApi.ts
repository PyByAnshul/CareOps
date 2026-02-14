import { apiClient } from '@/core/api/client'

export const bookingsApi = {
  list: (params?: any) => apiClient.get('/api/bookings', { params }).then(r => r.data),
  get: (id: string) => apiClient.get(`/api/bookings/${id}`).then(r => r.data),
  create: (data: any) => apiClient.post('/api/bookings', data).then(r => r.data),
  update: (id: string, data: any) => apiClient.put(`/api/bookings/${id}`, data).then(r => r.data),
  delete: (id: string) => apiClient.delete(`/api/bookings/${id}`),
  confirm: (id: number) => apiClient.post(`/api/bookings/${id}/confirm`).then(r => r.data),
  cancel: (id: number) => apiClient.post(`/api/bookings/${id}/cancel`).then(r => r.data),
  complete: (id: number) => apiClient.post(`/api/bookings/${id}/complete`).then(r => r.data),
}
