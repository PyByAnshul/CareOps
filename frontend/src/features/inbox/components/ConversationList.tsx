const statusColors = {
  pending: 'bg-yellow-100 text-yellow-700',
  replied: 'bg-green-100 text-green-700',
  closed: 'bg-slate-100 text-slate-700',
}

export function ConversationList({ conversations, selectedId, onSelect }: any) {
  return (
    <div>
      {conversations.map((conv: any) => (
        <button
          key={conv.id}
          onClick={() => onSelect(conv.id)}
          className={`w-full text-left p-4 border-b border-slate-200 hover:bg-slate-50 transition-colors ${
            selectedId === conv.id ? 'bg-blue-50' : ''
          }`}
        >
          <div className="flex justify-between items-start mb-1">
            <p className={`font-medium text-slate-900 ${conv.unread_count > 0 ? 'font-bold' : ''}`}>
              {conv.customer_name || conv.contact_email || 'Unknown'}
            </p>
            {conv.unread_count > 0 && (
              <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                {conv.unread_count}
              </span>
            )}
          </div>
          {conv.subject && <p className="text-sm text-slate-900 mb-1">{conv.subject}</p>}
          <div className="flex justify-between items-center">
            <span className={`text-xs px-2 py-1 rounded ${statusColors[conv.status as keyof typeof statusColors] || 'bg-slate-100 text-slate-700'}`}>
              {conv.status}
            </span>
            <span className="text-xs text-slate-500">
              {new Date(conv.last_message_at || conv.created_at).toLocaleDateString()}
            </span>
          </div>
        </button>
      ))}
    </div>
  )
}
