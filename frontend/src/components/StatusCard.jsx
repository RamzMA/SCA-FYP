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

      {phase === 'done' && result && <DoneSummary result={result} />}
    </section>
  )
}

function DoneSummary({ result }) {
  const recorded = result.attendance_recorded?.length ?? 0
  const already = result.duplicate_records ?? 0
  const total = recorded + already
  const sampled = (result.frames_processed ?? 0) + (result.frames_too_blurry ?? 0)

  return (
    <div className="stack">
      <div>
        <div className="headline">
          {total} {total === 1 ? 'student' : 'students'} found in this video
        </div>
        <div className="muted">
          {recorded} newly recorded
          {already > 0 ? `, ${already} already recorded for this date` : ''}.
        </div>
      </div>

      <div className="muted small">
        A student is only recorded if their card was clear enough to read at least once. If someone
        who attended is not in the table, their card was not readable in the video.
      </div>

      <details className="details">
        <summary>Processing details</summary>
        <div className="tiles">
          <Tile value={sampled} label="Video moments sampled" />
          <Tile value={result.frames_too_blurry} label="Skipped as blurry" />
          <Tile value={result.frames_without_student} label="No card number visible" />
        </div>
        <div className="muted small">
          These are moments throughout the video where the system tried to read a card. It does not mean students were missed, just certain frames were not clear enough to read. 
        </div>
      </details>
    </div>
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
