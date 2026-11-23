import { useRef, useState } from 'react'

const ALLOWED = ['.mp4', '.mov', '.avi', '.mkv']

function hasAllowedExtension(name) {
  const lower = name.toLowerCase()
  return ALLOWED.some((ext) => lower.endsWith(ext))
}

export default function UploadCard({ file, onFile, date, onDate, onSubmit, busy }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [fileError, setFileError] = useState('')

  function choose(picked) {
    if (!picked) return
    if (!hasAllowedExtension(picked.name)) {
      setFileError('That file type is not supported. Use MP4, MOV, AVI or MKV.')
      onFile(null)
      return
    }
    setFileError('')
    onFile(picked)
  }

  {/*Prevent autoloading video with prevent default and choose first video if multiple added with datatransfer files[0]*/}
  function handleDrop(event) {
    event.preventDefault()
    setDragging(false)
    choose(event.dataTransfer.files[0])
  }

  return (
    <section className="card" aria-labelledby="upload-heading">
      <h2 id="upload-heading" className="card-title">
        Upload a lecture video
      </h2>

      <div className="field">
        <label htmlFor="lecture-date">Lecture date</label>
        <input
          id="lecture-date"
          type="date"
          value={date}
          onChange={(e) => onDate(e.target.value)}
          className="input date-input"
        />
      </div>

      <div
        className={`dropzone${dragging ? ' dropzone-active' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 16V5M7 9l5-5 5 5" />
          <path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
        </svg>
        {file ? (
          <div className="dropzone-title">{file.name}</div>
        ) : (
          <div className="dropzone-title">Drop a video here</div>
        )}
        <div className="muted small">MP4, MOV, AVI or MKV</div>
        <input
          ref={inputRef}
          type="file"
          accept=".mp4,.mov,.avi,.mkv,video/*"
          hidden
          onChange={(e) => choose(e.target.files[0])}
        />
        <button type="button" className="btn btn-outline" onClick={() => inputRef.current.click()}>
          {file ? 'Choose a different file' : 'Choose a file'}
        </button>
        {fileError && (
          <div role="alert" className="error-text">
            {fileError}
          </div>
        )}
      </div>

      <div className="card-footer">
        <div className="muted small footer-note">
          Each card shown to the camera is recorded once per lecture date.
        </div>
        <button type="button" className="btn btn-primary" onClick={onSubmit} disabled={!file || !date || busy}>
          {busy ? 'Working…' : 'Upload and process'}
        </button>
      </div>
    </section>
  )
}
