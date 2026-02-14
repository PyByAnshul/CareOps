import { apiClient } from '@/core/api/client'

export const inboxApi = {
  getConversations: (params?: any) => apiClient.get('/api/inbox/conversations', { params }).then(r => r.data),
  getConversation: (id: string) => apiClient.get(`/api/inbox/conversations/${id}`).then(r => r.data),
  sendMessage: (conversationId: string, data: { content: string }) => apiClient.post(`/api/inbox/conversations/${conversationId}/send`, data).then(r => r.data),
  updateConversation: (id: string, data: { status: string }) => apiClient.put(`/api/inbox/conversations/${id}`, data).then(r => r.data),
  syncGmail: () => apiClient.post('/api/inbox/sync-gmail').then(r => r.data),
}
