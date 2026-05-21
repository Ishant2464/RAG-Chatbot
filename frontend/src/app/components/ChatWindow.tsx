'use client'

import { useState, useRef, useEffect, KeyboardEvent } from 'react'
import MessageBubble from './MessageBubble'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

interface Props {
  fileUrl: string
}

export default function ChatWindow({ fileUrl }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: 'Document loaded. Ask me anything about it.',
    },
  ])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const API = process.env.NEXT_PUBLIC_API_URL

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage() {
    const query = input.trim()
    if (!query || isStreaming) return

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

    setMessages((prev) => [...prev, userMessage, assistantMessage])
    setInput('')
    setIsStreaming(true)

    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
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

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto max-w-2xl space-y-6">
          {messages.map((m, i) => (
            <MessageBubble
              key={m.id}
              role={m.role}
              content={m.content}
              isStreaming={isStreaming && i === messages.length - 1 && m.role === 'assistant'}
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
