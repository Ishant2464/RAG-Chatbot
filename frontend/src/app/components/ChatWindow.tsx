'use client'

import { useState, useRef, useEffect, KeyboardEvent } from 'react'
import MessageBubble from './MessageBubble'

interface Source {
  page: string
  snippet: string
  source: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  suggestions?: string[]
}

interface Props {
  fileUrl: string
  initialMessages?: Message[]
  onMessagesChange?: (messages: Message[]) => void
}

export default function ChatWindow({ fileUrl, initialMessages, onMessagesChange }: Props) {
  const [messages, setMessages] = useState<Message[]>(
    initialMessages && initialMessages.length > 0
      ? initialMessages
      : [
          {
            id: '0',
            role: 'assistant',
            content: 'Document loaded. Ask me anything about it.',
          },
        ]
  )
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const API = process.env.NEXT_PUBLIC_API_URL || 'https://rag-chatbot-d3wz.onrender.com'

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (onMessagesChange && messages.length > 1) {
      onMessagesChange(messages)
    }
  }, [messages])

  async function executeSend(query: string) {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
    }

    const assistantId = (Date.now() + 1).toString()
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
    }

    // Prepare messages for the backend, filtering out the initial welcome message
    // and limiting to the last 20 messages for context window management.
    const allMessages = [...messages.filter(m => m.id !== '0'), userMessage]
    const recentMessages = allMessages.slice(-20) // Limit to last 20 messages

    const payloadMessages = recentMessages.map(m => ({
      role: m.role,
      content: m.content
    }))

    setMessages((prev) => [...prev, userMessage, assistantMessage])
    setIsStreaming(true)

    // Start sources fetch (non-blocking, parallel to streaming)
    fetch(`${API}/chat/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, file_url: fileUrl }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.sources) {
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId ? { ...m, sources: data.sources } : m
            )
          )
        }
      })
      .catch(err => console.error('Sources fetch error:', err))

    // Start suggestions fetch (non-blocking, parallel to streaming)
    fetch(`${API}/chat/suggestions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: payloadMessages, file_url: fileUrl }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.suggestions) {
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId ? { ...m, suggestions: data.suggestions } : m
            )
          )
        }
      })
      .catch(err => console.error('Suggestions fetch error:', err))

    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: payloadMessages,
          file_url: fileUrl,
        }),
      })

      if (!res.ok) throw new Error('Stream request failed')
      if (!res.body) throw new Error('No response body')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + chunk } : m
          )
        )
      }
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: 'Something went wrong. Please try again.' }
            : m
        )
      )
    } finally {
      setIsStreaming(false)
    }
  }

  function sendMessage() {
    if (!input.trim() || isStreaming) return
    executeSend(input.trim())
    setInput('')
  }

  function handleSuggestionClick(suggestion: string) {
    if (!isStreaming) {
      executeSend(suggestion)
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  function exportChat() {
    const chatContent = messages
      .filter(m => m.id !== '0') // Skip welcome message
      .map(m => {
        const role = m.role === 'user' ? '## 🧑 You' : '## 🤖 AI'
        let text = `${role}\n\n${m.content}`
        if (m.sources && m.sources.length > 0) {
          text += '\n\n**Sources:** ' + m.sources.map(s => `Page ${s.page}`).join(', ')
        }
        return text
      })
      .join('\n\n---\n\n')

    const header = `# RAG Chatbot Conversation\n\nExported: ${new Date().toLocaleString()}\n\n---\n\n`
    const fullContent = header + chatContent

    const blob = new Blob([fullContent], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rag-chat-${new Date().toISOString().slice(0, 10)}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex items-center justify-between px-6 py-2 border-b border-gray-800">
        <span className="text-xs text-gray-500">Chat with your document</span>
        <button
          onClick={exportChat}
          disabled={messages.filter(m => m.id !== '0').length === 0 || isStreaming}
          className="text-xs text-gray-400 hover:text-white flex items-center gap-1.5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          title="Export chat as Markdown"
        >
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto max-w-2xl space-y-6">
          {messages.map((m, i) => (
            <MessageBubble
              key={m.id}
              role={m.role}
              content={m.content}
              sources={m.sources}
              suggestions={m.suggestions}
              isStreaming={isStreaming && i === messages.length - 1 && m.role === 'assistant'}
              isLastAssistant={m.role === 'assistant' && i === messages.length - 1}
              onSuggestionClick={handleSuggestionClick}
            />
          ))}
          <div ref={bottomRef} />
        </div>
      </div>

      <div className="border-t border-gray-800 px-6 py-4">
        <div className="mx-auto max-w-2xl">
          <div className="flex gap-3 items-end">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question... (Enter to send)"
              rows={1}
              disabled={isStreaming}
              className="
                flex-1 resize-none rounded-xl bg-gray-800 px-4 py-3 text-sm text-gray-100
                placeholder-gray-500 outline-none focus:ring-1 focus:ring-blue-500
                disabled:opacity-50 max-h-32 overflow-y-auto
              "
              style={{ minHeight: '44px' }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isStreaming}
              className="
                flex h-11 w-11 shrink-0 items-center justify-center rounded-xl
                bg-blue-600 text-white transition-colors
                hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed
              "
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
              </svg>
            </button>
          </div>
          <p className="mt-2 text-xs text-gray-600 text-center">
            Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}
