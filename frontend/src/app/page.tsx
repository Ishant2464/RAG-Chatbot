'use client'

import { useState, useEffect } from 'react'
import { useAuth } from './components/AuthProvider'
import LoginScreen from './components/LoginScreen'
import DocumentSidebar from './components/DocumentSidebar'
import FileUpload from './components/FileUpload'
import ChatWindow from './components/ChatWindow'

interface Document {
  url: string
  name: string
  uploadedAt: string
}

export default function Home() {
  const { user, loading, signOut } = useAuth()
  const [fileUrl, setFileUrl] = useState<string | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [showUpload, setShowUpload] = useState(false)
  const [chatHistories, setChatHistories] = useState<Record<string, any[]>>({})

  // Load documents from localStorage on mount (per-user)
  useEffect(() => {
    if (user) {
      const saved = localStorage.getItem(`rag-docs-${user.id}`)
      if (saved) {
        try {
          setDocuments(JSON.parse(saved))
        } catch {}
      }
    }
  }, [user])

  // Save documents to localStorage when they change
  useEffect(() => {
    if (user && documents.length > 0) {
      localStorage.setItem(`rag-docs-${user.id}`, JSON.stringify(documents))
    }
  }, [documents, user])

  // Handle new document upload success
  function handleUploadSuccess(url: string, fileName: string) {
    const newDoc: Document = {
      url,
      name: fileName,
      uploadedAt: new Date().toISOString(),
    }
    setDocuments((prev) => [newDoc, ...prev])
    setFileUrl(url)
    setShowUpload(false)
  }

  // Handle document selection from sidebar
  function handleSelectDocument(url: string) {
    setFileUrl(url)
    setShowUpload(false)
  }

  function handleMessagesChange(url: string, messages: any[]) {
    setChatHistories(prev => ({ ...prev, [url]: messages }))
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-700 border-t-blue-400" />
      </div>
    )
  }

  if (!user) {
    return <LoginScreen />
  }

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white">RAG Chatbot</h1>
            <p className="text-sm text-gray-400">Upload a PDF and ask questions about it</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${fileUrl ? 'bg-green-400' : 'bg-gray-600'}`} />
              <span className="text-sm text-gray-400">
                {fileUrl ? 'Document ready' : 'No document loaded'}
              </span>
            </div>
            <div className="flex items-center gap-3 border-l border-gray-700 pl-4">
              {user.user_metadata?.avatar_url && (
                <img
                  src={user.user_metadata.avatar_url}
                  alt="Profile"
                  className="h-7 w-7 rounded-full"
                />
              )}
              <span className="text-sm text-gray-300">
                {user.user_metadata?.full_name || user.email}
              </span>
              <button
                onClick={signOut}
                className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <DocumentSidebar
          documents={documents}
          activeUrl={fileUrl}
          onSelectDocument={handleSelectDocument}
          onNewUpload={() => setShowUpload(true)}
        />
        <main className="flex flex-1 overflow-hidden">
          <div className="flex w-full flex-col">
            {showUpload || !fileUrl ? (
              <div className="flex flex-1 items-center justify-center p-8">
                <FileUpload onSuccess={handleUploadSuccess} />
              </div>
            ) : (
              <ChatWindow
                key={fileUrl}
                fileUrl={fileUrl}
                initialMessages={chatHistories[fileUrl!] || undefined}
                onMessagesChange={(msgs: any[]) => handleMessagesChange(fileUrl!, msgs)}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
