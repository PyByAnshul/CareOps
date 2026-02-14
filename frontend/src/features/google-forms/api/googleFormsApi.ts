import { apiClient } from '@/core/api/client'

export const googleFormsApi = {
  list: () => apiClient.get('/api/google-forms').then(r => r.data),
  get: (id: number) => apiClient.get(`/api/google-forms/${id}`).then(r => r.data),
  create: (data: any) => apiClient.post('/api/google-forms', data).then(r => r.data),
  update: (id: number, data: any) => apiClient.put(`/api/google-forms/${id}`, data).then(r => r.data),
  delete: (id: number) => apiClient.delete(`/api/google-forms/${id}`),
  getSubmissions: (id: number) => apiClient.get(`/api/google-forms/${id}/submissions`).then(r => r.data),
}
