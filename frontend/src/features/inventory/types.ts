export interface Product {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  unit: string;
  reorder_level: number;
  created_at: string;
  updated_at: string;
}

export interface StockMovement {
  id: string;
  product_id: string;
  type: 'in' | 'out';
  quantity: number;
  reason: string;
  created_at: string;
}

export interface ProcurementOrder {
  id: string;
  product_id: string;
  quantity: number;
  status: string;
  created_at: string;
}
