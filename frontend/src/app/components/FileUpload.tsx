'use client'

import { useState, useRef, DragEvent, ChangeEvent } from 'react'

interface Props {
  onSuccess: (url: string) => void
}

type Status = 'idle' | 'uploading' | 'polling' | 'done' | 'error'

export default function FileUpload({ onSuccess }: Props) {
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [fileName, setFileName] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const API = process.env.NEXT_PUBLIC_API_URL

  async function uploadFile(file: File) {
    if (!file.name.endsWith('.pdf')) {
      setStatus('error')
      setMessage('Only PDF files are supported.')
      return
    }

    setFileName(file.name)
    setStatus('uploading')
    setMessage('Uploading...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API}/ingest`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed')
      }

      setStatus('polling')
      setMessage('Processing document...')
      pollStatus(data.job_id, data.storage_url)
    } catch (err: unknown) {
      setStatus('error')
      setMessage(err instanceof Error ? err.message : 'Upload failed')
    }
  }

  async function pollStatus(jobId: string, storageUrl: string) {
    for (let i = 0; i < 60; i++) {
      try {
        const res = await fetch(`${API}/ingest/${jobId}/status`)
        const data = await res.json()

        if (data.status === 'finished') {
          setStatus('done')
          setMessage('✅ Document ready!')
          onSuccess(storageUrl)
          return
        }

        if (data.status === 'failed') {
          setStatus('error')
          setMessage(`Processing failed: ${data.error}`)
          return
        }
      } catch (err) {
        console.error('Poll error:', err)
      }

      await new Promise((resolve) => setTimeout(resolve, 1000))
    }

    setStatus('error')
    setMessage('Processing timeout')
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault()
    setIsDragging(true)
  }

  function handleDragLeave() {
    setIsDragging(false)
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) uploadFile(files[0])
  }

  return (
    <div className="w-full max-w-md rounded-lg border-2 border-dashed border-gray-600 p-8 text-center">
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={(e: ChangeEvent<HTMLInputElement>) => {
          if (e.target.files?.length) uploadFile(e.target.files[0])
        }}
        className="hidden"
      />

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer transition ${isDragging ? 'bg-gray-700' : ''}`}
      >
        <div className="mb-4 text-4xl">📄</div>
        <h3 className="mb-2 text-lg font-semibold text-white">
          {status === 'uploading' || status === 'polling' ? 'Processing...' : 'Upload PDF'}
        </h3>
        <p className="mb-4 text-sm text-gray-400">{message || 'Drag and drop or click to select'}</p>

        {status === 'idle' && (
          <button
            type="button"
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Choose File
          </button>
        )}
      </div>
    </div>
  )
}
    } catch (err: unknown) {
      setStatus('error')
      setMessage(err instanceof Error ? err.message : 'Upload failed')
    }
  }

  async function pollStatus(jobId: string) {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/ingest/${jobId}/status`)
        const data = await res.json()

        if (data.status === 'finished') {
          clearInterval(interval)
          setStatus('done')
          setMessage('Document ready.')
          setTimeout(onSuccess, 800)
        } else if (data.status === 'failed') {
          clearInterval(interval)
          setStatus('error')
          setMessage('Processing failed. Try again.')
        }
      } catch {
        clearInterval(interval)
        setStatus('error')
        setMessage('Status check failed.')
      }
    }, 2000)
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) uploadFile(file)
  }

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) uploadFile(file)
  }

  const isLoading = status === 'uploading' || status === 'polling'

  return (
    <div className="w-full max-w-lg">
      <div
        onClick={() => !isLoading && inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        className={`
          relative flex flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed p-12
          transition-colors cursor-pointer
          ${isDragging ? 'border-blue-400 bg-blue-950/30' : 'border-gray-700 bg-gray-900 hover:border-gray-500'}
          ${isLoading ? 'cursor-not-allowed opacity-70' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleChange}
          disabled={isLoading}
        />

        {status === 'idle' && (
          <>
            <div className="rounded-full bg-gray-800 p-4">
              <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-base font-medium text-gray-200">Drop your PDF here</p>
              <p className="mt-1 text-sm text-gray-500">or click to browse</p>
            </div>
          </>
        )}

        {isLoading && (
          <>
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-gray-700 border-t-blue-400" />
            <div className="text-center">
              <p className="text-sm font-medium text-gray-200">{fileName}</p>
              <p className="mt-1 text-sm text-gray-400">{message}</p>
            </div>
          </>
        )}

        {status === 'done' && (
          <>
            <div className="rounded-full bg-green-900/50 p-4">
              <svg className="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-sm text-green-400">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="rounded-full bg-red-900/50 p-4">
              <svg className="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="text-sm text-red-400">{message}</p>
            <button
              onClick={(e) => { e.stopPropagation(); setStatus('idle'); setMessage('') }}
              className="text-xs text-gray-500 underline hover:text-gray-300"
            >
              Try again
            </button>
          </>
        )}
      </div>
    </div>
  )
}
