import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface Source {
  page: string
  snippet: string
  source: string
}

interface Props {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  suggestions?: string[]
  isStreaming?: boolean
  isLastAssistant?: boolean
  onSuggestionClick?: (suggestion: string) => void
}

export default function MessageBubble({ role, content, sources, suggestions, isStreaming, isLastAssistant, onSuggestionClick }: Props) {
  const isUser = role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`
        flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold
        ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}
      `}>
        {isUser ? 'You' : 'AI'}
      </div>

      <div className={`
        max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed
        ${isUser
          ? 'bg-blue-600 text-white rounded-tr-sm'
          : 'bg-gray-800 text-gray-100 rounded-tl-sm'
        }
      `}>
        {isUser ? (
          content
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                    customStyle={{
                      margin: '0.5rem 0',
                      borderRadius: '0.5rem',
                      fontSize: '0.8rem',
                    }}
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code
                    className="bg-gray-700 text-gray-200 px-1.5 py-0.5 rounded text-sm font-mono"
                    {...props}
                  >
                    {children}
                  </code>
                )
              },
              p({ children }: any) {
                return <p className="mb-2 last:mb-0">{children}</p>
              },
              ul({ children }: any) {
                return <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
              },
              ol({ children }: any) {
                return <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
              },
              li({ children }: any) {
                return <li className="ml-2">{children}</li>
              },
              h1({ children }: any) {
                return <h1 className="text-lg font-bold mb-2">{children}</h1>
              },
              h2({ children }: any) {
                return <h2 className="text-base font-bold mb-2">{children}</h2>
              },
              h3({ children }: any) {
                return <h3 className="text-sm font-bold mb-1">{children}</h3>
              },
              blockquote({ children }: any) {
                return (
                  <blockquote className="border-l-2 border-gray-500 pl-3 italic text-gray-300 mb-2">
                    {children}
                  </blockquote>
                )
              },
              table({ children }: any) {
                return (
                  <div className="overflow-x-auto mb-2">
                    <table className="min-w-full text-sm border border-gray-600">
                      {children}
                    </table>
                  </div>
                )
              },
              thead({ children }: any) {
                return <thead className="bg-gray-700">{children}</thead>
              },
              th({ children }: any) {
                return <th className="px-3 py-1 text-left font-semibold border border-gray-600">{children}</th>
              },
              td({ children }: any) {
                return <td className="px-3 py-1 border border-gray-600">{children}</td>
              },
              a({ href, children }: any) {
                return (
                  <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                    {children}
                  </a>
                )
              },
              strong({ children }: any) {
                return <strong className="font-semibold text-white">{children}</strong>
              },
              em({ children }: any) {
                return <em className="italic text-gray-300">{children}</em>
              },
              hr() {
                return <hr className="border-gray-600 my-2" />
              },
            }}
          >
            {content}
          </ReactMarkdown>
        )}
        {isStreaming && (
          <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-current opacity-70" />
        )}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <p className="text-xs text-gray-400 mb-2 font-medium">📄 Sources</p>
            <div className="flex flex-wrap gap-2">
              {sources.map((source, index) => (
                <div
                  key={index}
                  className="group relative"
                >
                  <div className="inline-flex items-center gap-1.5 rounded-lg bg-gray-700/50 px-2.5 py-1.5 text-xs text-gray-300 hover:bg-gray-700 hover:text-white transition-colors cursor-default">
                    <span className="text-blue-400">📄</span>
                    <span>Page {source.page}</span>
                  </div>
                  {/* Tooltip with snippet on hover */}
                  <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block z-50 w-64 p-3 rounded-lg bg-gray-900 border border-gray-700 shadow-xl">
                    <p className="text-xs text-gray-400 mb-1 font-medium">Page {source.page}</p>
                    <p className="text-xs text-gray-300 leading-relaxed">{source.snippet}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {!isUser && isLastAssistant && !isStreaming && suggestions && suggestions.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <p className="text-xs text-gray-400 mb-2 font-medium">💡 Follow-up questions</p>
            <div className="flex flex-col gap-1.5">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => onSuggestionClick?.(suggestion)}
                  className="text-left text-xs text-blue-400 hover:text-blue-300 hover:bg-gray-700/50 rounded-lg px-2.5 py-1.5 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
