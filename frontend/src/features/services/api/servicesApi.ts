import { apiClient } from '@/core/api/client';

export const servicesApi = {
  list: async () => {
    const response = await apiClient.get('/api/services');
    return response.data;
  },
  get: async (id: number) => {
    const response = await apiClient.get(`/api/services/${id}`);
    return response.data;
  },
  create: async (data: any) => {
    const response = await apiClient.post('/api/services', data);
    return response.data;
  },
  update: async (id: number, data: any) => {
    const response = await apiClient.put(`/api/services/${id}`, data);
    return response.data;
  },
  delete: async (id: number) => {
    await apiClient.delete(`/api/services/${id}`);
  },
};
