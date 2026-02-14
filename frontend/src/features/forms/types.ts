export interface Form {
  id: string;
  name: string;
  form_type: 'booking' | 'inquiry' | 'quote';
  description: string;
  fields: any[];
  is_active: boolean;
  created_at: string;
}

export interface Inquiry {
  id: number;
  workspace_id: number;
  form_submission_id?: number;
  customer_name: string;
  customer_email: string;
  inquiry_type: 'inquiry' | 'quote';
  subject?: string;
  message?: string;
  status: 'new' | 'contacted' | 'converted' | 'closed';
  assigned_to?: number;
  created_at: string;
  updated_at: string;
}
