import BoardingPass from './BoardingPass'

function TypingIndicator() {
  return (
    <div className="flex items-end gap-3 msg-enter">
      <div className="w-8 h-8 rounded-full bg-navy-700 border border-sky-accent/30 flex items-center justify-center flex-shrink-0">
        <span className="text-sky-accent text-sm">✈</span>
      </div>
      <div className="glass-card rounded-2xl rounded-bl-sm px-4 py-3">
        <div className="flex gap-1.5 items-center h-4">
          <div className="typing-dot w-2 h-2 rounded-full bg-sky-accent/60" />
          <div className="typing-dot w-2 h-2 rounded-full bg-sky-accent/60" />
          <div className="typing-dot w-2 h-2 rounded-full bg-sky-accent/60" />
        </div>
      </div>
    </div>
  )
}

function formatText(text) {
  if (!text) return null
  // Bold markdown **text**
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, i) =>
    part.startsWith('**') && part.endsWith('**')
      ? <strong key={i} className="text-sky-accent font-semibold">{part.slice(2, -2)}</strong>
      : part.split('\n').map((line, j, arr) => (
        <span key={`${i}-${j}`}>{line}{j < arr.length - 1 && <br/>}</span>
      ))
  )
}

function PolicyCard({ policy }) {
  // FIX 3: policies.csv uses topic/rule_summary/rule_detail, not title/description
  const topicIcons = { baggage: '🧳', cancellation: '❌', refund: '💰', no_show: '🚫', change_fee: '✏️' }
  const icon = topicIcons[policy.topic] || '📋'
  const title = policy.rule_summary || policy.title || policy.topic
  const detail = policy.rule_detail || policy.description || ''
  const scope = policy.fare_class && policy.fare_class !== 'all' ? ` (${policy.fare_class} class)` : ''
  return (
    <div className="bg-navy-700/50 border border-white/10 rounded-xl p-3 mb-2">
      <div className="flex items-center gap-2 mb-1">
        <span>{icon}</span>
        <div className="text-xs font-semibold text-sky-accent">{title}{scope}</div>
      </div>
      <div className="text-xs text-gray-300 leading-relaxed">{detail}</div>
    </div>
  )
}

function BotMessage({ msg }) {
  if (msg.type === 'ticket') {
    return (
      <div className="flex items-start gap-3 msg-enter max-w-full">
        <div className="w-8 h-8 rounded-full bg-navy-700 border border-sky-accent/30 flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-sky-accent text-sm">✈</span>
        </div>
        <div className="flex-1 max-w-xs">
          {msg.message && (
            <div className="glass-card rounded-2xl rounded-bl-sm px-4 py-3 mb-3">
              <p className="text-sm leading-relaxed text-gray-200">{formatText(msg.message)}</p>
            </div>
          )}
          <BoardingPass ticket={msg} compact={false} />
        </div>
      </div>
    )
  }

  if (msg.type === 'bookings') {
    return (
      <div className="flex items-start gap-3 msg-enter max-w-full">
        <div className="w-8 h-8 rounded-full bg-navy-700 border border-sky-accent/30 flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-sky-accent text-sm">✈</span>
        </div>
        <div className="flex-1 max-w-xs">
          <div className="glass-card rounded-2xl rounded-bl-sm px-4 py-3 mb-3">
            <p className="text-sm text-gray-200">{formatText(msg.message)}</p>
          </div>
          {msg.bookings.map((b, i) => (
            <div key={i} className="mb-3"><BoardingPass ticket={b} compact={true} /></div>
          ))}
        </div>
      </div>
    )
  }

  if (msg.type === 'policies') {
    return (
      <div className="flex items-start gap-3 msg-enter max-w-full">
        <div className="w-8 h-8 rounded-full bg-navy-700 border border-sky-accent/30 flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-sky-accent text-sm">✈</span>
        </div>
        <div className="flex-1 max-w-sm">
          <div className="glass-card rounded-2xl rounded-bl-sm px-4 py-3 mb-3">
            <p className="text-sm text-gray-200">{formatText(msg.message)}</p>
          </div>
          {msg.policies?.map((p, i) => <PolicyCard key={i} policy={p} />)}
        </div>
      </div>
    )
  }

  // Default text response
  return (
    <div className="flex items-end gap-3 msg-enter">
      <div className="w-8 h-8 rounded-full bg-navy-700 border border-sky-accent/30 flex items-center justify-center flex-shrink-0">
        <span className="text-sky-accent text-sm">✈</span>
      </div>
      <div className="glass-card rounded-2xl rounded-bl-sm px-4 py-3 max-w-xs">
        <p className="text-sm leading-relaxed text-gray-200">{formatText(msg.message || msg.text || '')}</p>
      </div>
    </div>
  )
}

function UserMessage({ msg }) {
  return (
    <div className="flex items-end gap-3 justify-end msg-enter">
      <div className="bg-gradient-to-br from-navy-600 to-navy-500 rounded-2xl rounded-br-sm px-4 py-3 max-w-xs">
        <p className="text-sm text-white">{msg.text}</p>
      </div>
      <div className="w-8 h-8 rounded-full bg-navy-600 border border-white/20 flex items-center justify-center flex-shrink-0 text-white text-xs font-bold flex-shrink-0">
        {msg.initials || 'U'}
      </div>
    </div>
  )
}

export { BotMessage, UserMessage, TypingIndicator }
