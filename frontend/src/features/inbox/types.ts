export interface Message {
  id: string
  conversationId: string
  senderId: string
  senderName: string
  content: string
  createdAt: string
}

export interface Conversation {
  id: string
  participantIds: string[]
  lastMessage?: string
  lastMessageAt?: string
  subject?: string
  unreadCount: number
  createdAt: string
}
