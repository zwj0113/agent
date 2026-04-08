'use client'

import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Message = {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  events?: StreamEvent[]
}

type StreamEvent = {
  type: 'thought' | 'call' | 'answer' | 'error'
  content?: string
  tool?: string
  args?: Record<string, any>
}

export default function ChatApp() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [sessionId] = useState(() => Math.random().toString(36).substring(7))
  const [currentEvents, setCurrentEvents] = useState<StreamEvent[]>([])
  const [showThought, setShowThought] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, currentEvents])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isStreaming) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsStreaming(true)
    setCurrentEvents([])

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
        }),
      })

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let partialLine = ''

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        events: [],
      }

      setMessages(prev => [...prev, assistantMessage])

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = (partialLine + chunk).split('\n')
        partialLine = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('event:')) {
            // Event type line - we use 'message' as the event name
            continue
          }
          if (line.startsWith('data:')) {
            const data = line.slice(5).trim()
            if (!data) continue

            try {
              const event: StreamEvent = JSON.parse(data)
              setCurrentEvents(prev => [...prev, event])

              // Update assistant message
              if (event.type === 'answer' && event.content) {
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessage.id
                      ? { ...msg, content: msg.content + event.content, events: [...(msg.events || []), event] }
                      : msg
                  )
                )
              } else if (event.type === 'thought' || event.type === 'call') {
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessage.id
                      ? { ...msg, events: [...(msg.events || []), event] }
                      : msg
                  )
                )
              }
            } catch (parseError) {
              console.error('Parse error:', parseError)
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream error:', error)
      setMessages(prev =>
        prev.map(msg =>
          msg.id === (messages[messages.length - 1]?.id)
            ? { ...msg, content: 'Error: Failed to get response' }
            : msg
        )
      )
    } finally {
      setIsStreaming(false)
      setCurrentEvents([])
    }
  }

  return (
    <div className="flex h-screen">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b border-border px-6 py-4 bg-surface">
          <h1 className="text-xl font-semibold text-primary">AI Agent</h1>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <p className="text-lg mb-2">Welcome to AI Agent</p>
                <p className="text-sm">Ask me anything! I can use tools like a calculator.</p>
              </div>
            </div>
          )}

          {messages.map(msg => (
            <div key={msg.id} className="space-y-2">
              {/* User Message */}
              {msg.role === 'user' && (
                <div className="flex justify-end">
                  <div className="user-message message-bubble text-white max-w-xl">
                    {msg.content}
                  </div>
                </div>
              )}

              {/* Assistant Message */}
              {msg.role === 'assistant' && (
                <div className="space-y-2">
                  {/* All Events in chronological order (calls + thoughts) */}
                  {msg.events && msg.events.length > 0 && (
                    <div className="ml-4 space-y-1">
                      {msg.events.map((event, idx) => {
                        if (event.type === 'call') {
                          return (
                            <div key={idx} className="flex items-center gap-2 bg-gray-800/50 rounded px-3 py-2">
                              <span className="call-tag">🔧 {event.tool}</span>
                              {event.args && (
                                <span className="text-xs text-gray-400">{JSON.stringify(event.args)}</span>
                              )}
                              {event.result && (
                                <span className="text-xs text-green-400 ml-2">→ {String(event.result).substring(0, 80)}</span>
                              )}
                            </div>
                          );
                        }
                        if (event.type === 'thought') {
                          return (
                            <div key={idx} className="bg-gray-900/50 rounded px-3 py-2 text-sm">
                              <span className="text-yellow-400 text-xs">💭 </span>
                              <span className="text-gray-300">{event.content}</span>
                            </div>
                          );
                        }
                        return null;
                      })}
                    </div>
                  )}

                  {/* Final Answer */}
                  <div className="assistant-message message-bubble text-white">
                    {msg.content ? (
                      <div className="prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code: ({ className, children, ...props }) => {
                              const isInline = !className
                              return isInline ? (
                                <code className="bg-gray-800 px-1 py-0.5 rounded text-primary" {...props}>
                                  {children}
                                </code>
                              ) : (
                                <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto">
                                  <code className="text-gray-300">{children}</code>
                                </pre>
                              )
                            },
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="typing-cursor text-gray-400">Waiting for response...</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Current Streaming Events */}
          {isStreaming && currentEvents.length > 0 && (
            <div className="assistant-message message-bubble border-primary/50">
              <div className="space-y-1">
                {currentEvents.map((event, idx) => {
                  if (event.type === 'call') {
                    return (
                      <div key={idx} className="flex items-center gap-2 bg-gray-800/50 rounded px-3 py-2">
                        <span className="call-tag">🔧 {event.tool}</span>
                        {event.args && (
                          <span className="text-xs text-gray-400">{JSON.stringify(event.args)}</span>
                        )}
                        {event.result && (
                          <span className="text-xs text-green-400 ml-2">→ {String(event.result).substring(0, 80)}</span>
                        )}
                      </div>
                    );
                  }
                  if (event.type === 'thought') {
                    return (
                      <div key={idx} className="bg-gray-900/50 rounded px-3 py-2 text-sm">
                        <span className="text-yellow-400 text-xs">💭 </span>
                        <span className="text-gray-300">{event.content}</span>
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-border p-4 bg-surface">
          <form onSubmit={handleSubmit} className="flex gap-4 max-w-4xl mx-auto">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask me anything..."
              disabled={isStreaming}
              className="flex-1 bg-background border border-border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-primary disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isStreaming || !input.trim()}
              className="bg-primary hover:bg-primary/90 text-black font-medium px-6 py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isStreaming ? 'Thinking...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
