import apiClient from '@/core/api/client'

export const authApi = {
  register: (data: { email: string; password: string; workspace_id: number; role?: string }) =>
    apiClient.post('/api/users/register', data).then(r => r.data),
  login: (data: { email: string; password: string }) =>
    apiClient.post('/api/users/login', data).then(r => r.data),
  getMe: () =>
    apiClient.get('/api/users/me').then(r => r.data),
}
