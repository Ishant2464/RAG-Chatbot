'use client'

import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ChatWindow from './components/ChatWindow'

export default function Home() {
  const [fileUrl, setFileUrl] = useState<string | null>(null)

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="mx-auto max-w-4xl flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white">RAG Chatbot</h1>
            <p className="text-sm text-gray-400">Upload a PDF and ask questions about it</p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${fileUrl ? 'bg-green-400' : 'bg-gray-600'}`} />
            <span className="text-sm text-gray-400">
              {fileUrl ? 'Document ready' : 'No document loaded'}
            </span>
          </div>
        </div>
      </header>

      <main className="flex flex-1 overflow-hidden">
        <div className="mx-auto flex w-full max-w-4xl flex-col gap-0">
          {!fileUrl ? (
            <div className="flex flex-1 items-center justify-center p-8">
              <FileUpload onSuccess={(url: string) => setFileUrl(url)} />
            </div>
          ) : (
            <ChatWindow fileUrl={fileUrl} />
          )}
        </div>
      </main>
    </div>
  )
}
