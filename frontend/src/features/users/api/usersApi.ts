import { apiClient } from '@/core/api/client'

export interface UserResponse {
  id: number
  email: string
  role: string
  workspace_id: number
  is_active: boolean
  created_at: string
}

export const usersApi = {
  list: () => apiClient.get<UserResponse[]>('/api/users/').then((r) => r.data),
  get: (id: string) => apiClient.get<UserResponse>(`/api/users/${id}`).then((r) => r.data),
  getPermissions: (userId: string) =>
    apiClient.get<{ id: number; name: string; description: string | null; module: string }[]>(
      `/api/users/${userId}/permissions`
    ).then((r) => r.data),
  getMyPermissions: () =>
    apiClient.get<string[]>('/api/users/me/permissions').then((r) => r.data),
}
