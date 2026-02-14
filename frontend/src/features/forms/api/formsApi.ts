import { apiClient } from '@/core/api/client'

export const formsApi = {
  list: (params?: any) => apiClient.get('/api/forms', { params }).then(r => r.data),
  get: (id: string) => apiClient.get(`/api/forms/${id}`).then(r => r.data),
  create: (data: any) => apiClient.post('/api/forms', data).then(r => r.data),
  update: (id: string, data: any) => apiClient.put(`/api/forms/${id}`, data).then(r => r.data),
  delete: (id: string) => apiClient.delete(`/api/forms/${id}`),
  getSubmissions: (id: string) => apiClient.get(`/api/forms/${id}/submissions`).then(r => r.data),
  getPublic: (token: string) => apiClient.get(`/public/forms/${token}`).then(r => r.data),
  submitPublic: (token: string, data: any) => apiClient.post(`/public/forms/${token}/submit`, data).then(r => r.data),
  listInquiries: (status?: string) => apiClient.get('/api/forms/inquiries/list', { params: { status } }).then(r => r.data),
  updateInquiry: (id: number, data: { status?: string; assigned_to?: number }) => 
    apiClient.put(`/api/forms/inquiries/${id}`, null, { params: data }).then(r => r.data),
}
