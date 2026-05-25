'use client'

interface Document {
  url: string
  name: string
  uploadedAt: string
}

interface Props {
  documents: Document[]
  activeUrl: string | null
  onSelectDocument: (url: string) => void
  onNewUpload: () => void
}

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export default function DocumentSidebar({
  documents,
  activeUrl,
  onSelectDocument,
  onNewUpload,
}: Props) {
  return (
    <div className="flex w-64 flex-col border-r border-gray-800 bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 p-4">
        <h2 className="text-sm font-semibold text-white">📚 Documents</h2>
        <button
          onClick={onNewUpload}
          className="text-xs bg-blue-600 hover:bg-blue-500 text-white rounded-lg px-3 py-1.5 transition-colors font-medium"
        >
          Upload New
        </button>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto p-2">
        {documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <p className="text-sm text-gray-500 mb-1">No documents yet</p>
            <p className="text-xs text-gray-600">Upload your first PDF to get started</p>
          </div>
        ) : (
          <div className="space-y-1">
            {documents.map((doc) => (
              <button
                key={doc.url}
                onClick={() => onSelectDocument(doc.url)}
                className={`w-full text-left flex items-start gap-2 rounded-lg px-3 py-2.5 transition-colors ${
                  activeUrl === doc.url
                    ? 'bg-gray-800 border-l-2 border-blue-500'
                    : 'hover:bg-gray-800/50'
                }`}
              >
                <span className="shrink-0 text-lg">📄</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate">{doc.name}</p>
                  <p className="text-xs text-gray-500">{formatDate(doc.uploadedAt)}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
