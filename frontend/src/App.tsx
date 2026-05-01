import { useEffect, useMemo, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { apiRequest } from './lib/api'
import type { ChatApiResponse, ChatHistoryItem } from './types'

type ChatRole = 'user' | 'assistant'

type ChatMessage = {
  id: string
  role: ChatRole
  content: string
}

function createId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: createId(),
      role: 'assistant',
      content: 'Hello. I am ready. Ask me anything and I will answer using Gemini.',
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const listRef = useRef<HTMLDivElement | null>(null)

  const turnsForApi = useMemo(
    () =>
      messages
        .filter((message, index) => !(index === 0 && message.role === 'assistant'))
        .map((message): ChatHistoryItem => ({ role: message.role, content: message.content })),
    [messages],
  )

  useEffect(() => {
    const container = listRef.current
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, [messages, isLoading])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || isLoading) {
      return
    }

    const userMessage: ChatMessage = {
      id: createId(),
      role: 'user',
      content: trimmed,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setError(null)
    setIsLoading(true)

    try {
      const response = await apiRequest<ChatApiResponse>('/api/chat', {
        method: 'POST',
        body: JSON.stringify({
          message: trimmed,
          history: turnsForApi,
        }),
      })

      const assistantMessage: ChatMessage = {
        id: createId(),
        role: 'assistant',
        content: response.reply,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unexpected error'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="chat-surface">
        <header className="chat-header">
          <div>
            <p className="eyebrow">LangChain + Gemini</p>
            <h1>Amzur AI Chatbot</h1>
            <p className="subtitle">A fast conversational UI backed by your Python API.</p>
          </div>
        </header>

        <div ref={listRef} className="message-list" aria-live="polite">
          {messages.map((message) => (
            <article key={message.id} className={`bubble-row ${message.role === 'user' ? 'bubble-user' : 'bubble-assistant'}`}>
              <div className="bubble">{message.content}</div>
            </article>
          ))}

          {isLoading ? (
            <article className="bubble-row bubble-assistant">
              <div className="bubble bubble-loading">Thinking</div>
            </article>
          ) : null}
        </div>

        <footer className="chat-footer">
          <form onSubmit={handleSubmit} className="composer">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              className="composer-input"
              placeholder="Ask a question..."
              rows={2}
              disabled={isLoading}
            />
            <button type="submit" className="composer-send" disabled={isLoading || input.trim().length === 0}>
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </form>

          {error ? <p className="error-text">{error}</p> : null}
        </footer>
      </section>
    </main>
  )
}

export default App
