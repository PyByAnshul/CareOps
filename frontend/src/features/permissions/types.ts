export interface Permission {
  id: string;
  name: string;
  description: string;
}

export interface UserPermission {
  user_id: string;
  permissions: string[];
}
