import { apiClient } from '@/core/api/client'

export const permissionsApi = {
  list: () => apiClient.get('/api/permissions').then(r => r.data),
  assignPermission: (data: { user_id: number; permission_name: string }) => 
    apiClient.post('/api/permissions/assign', data).then(r => r.data),
  removePermission: (data: { user_id: number; permission_name: string }) => 
    apiClient.post('/api/permissions/remove', data).then(r => r.data),
}
