'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { inboxApi } from '../api/inboxApi'
import { useState } from 'react'
import { Send, X } from 'lucide-react'

export function MessageThread({ conversationId }: { conversationId: string }) {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState('')

  const { data: conversation, isLoading } = useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => inboxApi.getConversation(conversationId),
  })

  const messages = conversation?.messages || []

  const sendMutation = useMutation({
    mutationFn: (content: string) => inboxApi.sendMessage(conversationId, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      setMessage('')
    },
  })

  const closeMutation = useMutation({
    mutationFn: () => inboxApi.updateConversation(conversationId, { status: 'closed' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  if (isLoading) {
    return (
      <div className="p-6 space-y-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-16 bg-slate-200 rounded animate-pulse"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-slate-200 flex justify-between items-center">
        <div>
          <h3 className="font-semibold text-slate-900">{conversation?.contact_email}</h3>
          <p className="text-xs text-slate-500">Status: {conversation?.status}</p>
        </div>
        <button
          onClick={() => closeMutation.mutate()}
          className="text-sm text-slate-600 hover:text-slate-900 flex items-center gap-1"
        >
          <X className="w-4 h-4" />
          Close
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-slate-500 py-8">
            No messages yet
          </div>
        ) : (
          messages.map((msg: any) => (
            <div
              key={msg.id}
              className={`flex ${msg.direction === 'outbound' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] rounded-lg p-4 ${
                  msg.direction === 'outbound'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-900'
                }`}
              >
                <div 
                  className="text-sm whitespace-pre-wrap break-words prose prose-sm max-w-none"
                  dangerouslySetInnerHTML={{ __html: msg.content }}
                />
                <p className={`text-xs mt-2 ${
                  msg.direction === 'outbound' ? 'text-blue-100' : 'text-slate-500'
                }`}>
                  {new Date(msg.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="p-4 border-t border-slate-200">
        <div className="flex gap-2">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            rows={3}
            className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none"
          />
          <button
            onClick={() => message.trim() && sendMutation.mutate(message)}
            disabled={!message.trim() || sendMutation.isPending}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white px-4 rounded-lg transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
