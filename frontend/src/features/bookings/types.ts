export type BookingStatus = 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled'

export interface Booking {
  id: string
  clientId: string
  clientName: string
  serviceId: string
  serviceName: string
  startDate: string
  endDate: string
  status: BookingStatus
  notes?: string
  createdAt: string
  updatedAt: string
}

export interface CreateBookingRequest {
  clientId: string
  serviceId: string
  startDate: string
  endDate: string
  notes?: string
}

export interface UpdateBookingRequest {
  status?: BookingStatus
  startDate?: string
  endDate?: string
  notes?: string
}
