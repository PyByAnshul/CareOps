import { apiClient } from '@/core/api/client'

export const integrationsApi = {
  list: () => apiClient.get('/api/integrations').then(r => r.data),
  get: (id: string) => apiClient.get(`/api/integrations/${id}`).then(r => r.data),
  create: (data: any) => apiClient.post('/api/integrations', data).then(r => r.data),
  update: (id: string, data: any) => apiClient.put(`/api/integrations/${id}`, data).then(r => r.data),
  disconnect: (id: string) => apiClient.delete(`/api/integrations/${id}`),
}
