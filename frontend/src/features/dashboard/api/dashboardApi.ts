import { apiClient } from '@/core/api/client'

export const dashboardApi = {
  getSummary: () => apiClient.get('/api/dashboard/summary').then(r => r.data),
  getBookingStats: () => apiClient.get('/api/dashboard/booking-stats').then(r => r.data),
  getInventoryStats: () => apiClient.get('/api/dashboard/inventory-stats').then(r => r.data),
}
