import { apiClient } from '@/core/api/client'

export const contactsApi = {
  list: (params?: any) => apiClient.get('/api/contacts', { params }).then(r => r.data),
  get: (id: string) => apiClient.get(`/api/contacts/${id}`).then(r => r.data),
  create: (data: any) => apiClient.post('/api/contacts', data).then(r => r.data),
  update: (id: string, data: any) => apiClient.put(`/api/contacts/${id}`, data).then(r => r.data),
  delete: (id: string) => apiClient.delete(`/api/contacts/${id}`),
  grantPortalAccess: (id: string, data: { email?: string; password: string }) =>
    apiClient.post(`/api/contacts/${id}/grant-portal-access`, data).then(r => r.data),
  revokePortalAccess: (id: string) => apiClient.post(`/api/contacts/${id}/revoke-portal-access`).then(r => r.data),
}
