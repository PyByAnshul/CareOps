export interface Contact {
  id: string
  name: string
  email: string
  phone?: string
  address?: string
  type: 'client' | 'vendor' | 'staff'
  portalAccessGranted?: boolean
  portalAccessToken?: string
  createdAt: string
  updatedAt: string
}

export interface CreateContactRequest {
  name: string
  email: string
  phone?: string
  address?: string
  type: 'client' | 'vendor' | 'staff'
}

export interface GrantPortalAccessRequest {
  contactId: string
}
