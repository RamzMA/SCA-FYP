import { useCallback, useEffect, useRef, useState } from 'react'
import { getJob, getRecords, uploadVideo } from './api'
import UploadCard from './components/UploadCard'
import StatusCard from './components/StatusCard'
import RecordsSection from './components/RecordsSection'
import './App.css'

// Today as YYYY-MM-DD in the user's own time zone 
const today = () => new Date().toLocaleDateString('en-CA')

export default function App() {
  const [lectureDate, setLectureDate] = useState(today)
  const [file, setFile] = useState(null)
  const [phase, setPhase] = useState('idle')
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(null)
  const startedAt = useRef(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [records, setRecords] = useState(null)
  const [recordsError, setRecordsError] = useState('')

  const loadRecords = useCallback(async () => {
    try {
      setRecords(await getRecords())
      setRecordsError('')
    } catch (err) {
      setRecordsError(err.message)
    }
  }, [])

  // Load the table once when the page opens.
  useEffect(() => {
    loadRecords()
  }, [loadRecords])

  // While a job is running, ask the backend for its status every 2 seconds.
  useEffect(() => {
    if (!jobId) return
    let cancelled = false
    let timer

    async function poll() {
      try {
        const job = await getJob(jobId)
        if (cancelled) return
        const status = String(job.status).toLowerCase()

        if (status === 'done') {
          setResult(job.result)
          setPhase('done')
          loadRecords()
          return
        }
        if (status === 'failed') {
          setError(job.error || 'Processing failed.')
          setPhase('failed')
          return
        }
        setProgress(typeof job.progress === 'number' ? job.progress : null)
        setPhase('processing')
      } catch (err) {
        if (cancelled) return
        setError(err.message)
        setPhase('failed')
        return
      }
      timer = setTimeout(poll, 2000)
    }

    poll()
    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [jobId, loadRecords])

  async function handleSubmit() {
    if (!file) return
    setError('')
    setResult(null)
    setProgress(null)
    startedAt.current = Date.now()
    setPhase('uploading')
    try {
      setJobId(await uploadVideo(file, lectureDate))
    } catch (err) {
      setError(err.message)
      setPhase('failed')
    }
  }

  const busy = phase === 'uploading' || phase === 'processing'

  return (
    <div className="page">
      <header className="page-header">
        <h1>Lecture attendance</h1>
        <div className="muted">Signed in as lecturer</div>
      </header>

      <div className="card-row">
        <UploadCard
          file={file}
          onFile={setFile}
          date={lectureDate}
          onDate={setLectureDate}
          onSubmit={handleSubmit}
          busy={busy}
        />
        <StatusCard
          phase={phase}
          result={result}
          error={error}
          fileName={file?.name}
          progress={progress}
          startedAt={startedAt.current}
        />
      </div>

      <RecordsSection records={records} error={recordsError} onRetry={loadRecords} />
    </div>
  )
}
