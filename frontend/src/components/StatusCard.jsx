export default function StatusCard({ phase, result, error, fileName }) {
  return (
    <section className="card" aria-labelledby="status-heading" aria-live="polite">
      <h2 id="status-heading" className="card-title">
        Latest upload
      </h2>

      {phase === 'idle' && (
        <div className="empty-box">Add a lecture video to start.</div>
      )}

      {(phase === 'uploading' || phase === 'processing') && (
        <div className="stack">
          <div>
            {phase === 'uploading'
              ? `Uploading ${fileName ?? 'video'}`
              : 'Reading cards from the video.'}
          </div>
          <div className="progress" role="progressbar" aria-label="Processing">
            <div className="progress-bar" />
          </div>
          <div className="muted small">This page checks again every few seconds.</div>
        </div>
      )}

      {phase === 'failed' && (
        <div role="alert" className="error-box">
          <strong>Something went wrong.</strong>
          <div>{error}</div>
        </div>
      )}

      {phase === 'done' && result && (
        <div className="stack">
          <div className="tiles">
            <Tile value={result.frames_processed} label="Frames checked" />
            <Tile value={result.frames_too_blurry} label="Too blurry" />
            <Tile value={result.frames_without_student} label="No number read" />
            <Tile value={result.attendance_recorded?.length ?? 0} label="Recorded" />
            <Tile value={result.duplicate_records} label="Already recorded" />
          </div>
          <div className="muted small">
            Blurry frames and frames with no readable student number are not recorded.
          </div>
        </div>
      )}
    </section>
  )
}

function Tile({ value, label }) {
  return (
    <div className="tile">
      <div className="tile-value">{value ?? 0}</div>
      <div className="tile-label">{label}</div>
    </div>
  )
}
