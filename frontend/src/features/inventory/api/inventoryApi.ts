import { apiClient } from '@/core/api/client';

export const inventoryApi = {
  listProducts: async (params?: any) => {
    const response = await apiClient.get('/api/inventory/products', { params });
    return response.data;
  },
  getProduct: async (id: string) => {
    const response = await apiClient.get(`/api/inventory/products/${id}`);
    return response.data;
  },
  createProduct: async (data: any) => {
    const response = await apiClient.post('/api/inventory/products', data);
    return response.data;
  },
  updateProduct: async (id: string, data: any) => {
    const response = await apiClient.put(`/api/inventory/products/${id}`, data);
    return response.data;
  },
  deleteProduct: async (id: string) => {
    const response = await apiClient.delete(`/api/inventory/products/${id}`);
    return response.data;
  },
  listStockMovements: async (params?: any) => {
    const response = await apiClient.get('/api/inventory/stock-movements', { params });
    return response.data;
  },
  createStockMovement: async (data: any) => {
    const response = await apiClient.post('/api/inventory/stock-movements', data);
    return response.data;
  },
  listProcurementOrders: async (params?: any) => {
    const response = await apiClient.get('/api/inventory/procurement', { params });
    return response.data;
  },
  createProcurementOrder: async (data: any) => {
    const response = await apiClient.post('/api/inventory/procurement', data);
    return response.data;
  },
};
