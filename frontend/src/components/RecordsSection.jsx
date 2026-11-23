import { useMemo, useState } from 'react'
import { CSV_URL } from '../api'

// Change "2026-11-05" -> "5 Nov" for simplicity
function shortDate(iso) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString('en-IE', { day: 'numeric', month: 'short' })
}

export default function RecordsSection({ records, error, onRetry }) {
  const [query, setQuery] = useState('')

  //use memo to avoid recalculating the filtered rows on every render unless records or query changes.
  const rows = useMemo(() => {
    if (!records) return []
    const q = query.trim().toLowerCase()
    return records.students.filter(
      // !q means no query, so include all students otherwise check if the student number includes the query or if the name includes the query.
      (s) => !q || s.number.includes(q) || (s.name ?? '').toLowerCase().includes(q),
    )
  }, [records, query])

  // use date from records if available, otherwise default to empty array to avoid errors when mapping over dates.
  const dates = records?.dates ?? []

  return (
    <section className="records" aria-labelledby="records-heading">
      <div className="section-bar">
        <h2 id="records-heading" className="section-title">
          Records
        </h2>
        <div className="toolbar">
          <label htmlFor="search" className="sr-only">
            Search students
          </label>
          <input
            id="search"
            type="search"
            placeholder="Search name or number"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="input search-input"
          />
          <a href={CSV_URL} download="attendance.csv" className="btn btn-outline-accent">
            Download CSV
          </a>
        </div>
      </div>

      {/*Error if no records are available */}
      {error && (
        <div role="alert" className="error-box">
          <strong>Could not load the records.</strong>
          <div>{error}</div>
          <div>Check that the backend is running</div>
          <button type="button" className="btn btn-outline" onClick={onRetry}>
            Try again
          </button>
        </div>
      )}

      {/*Not error but no records available */}
      {!error && records && records.students.length === 0 && (
        <div className="empty-box">No attendance recorded yet.</div>
      )}

      {/*Records available*/}
      {!error && records && records.students.length > 0 && (
        <>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th scope="col">Number</th>
                  <th scope="col">Name</th>
                  {dates.map((d) => (
                    <th key={d} scope="col">
                      {shortDate(d)}
                    </th>
                  ))}
                  <th scope="col">Total</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((s) => (
                  <tr key={s.number}>
                    <td className="mono">{s.number}</td>
                    <td>{s.name || <span className="muted">Unavailable</span>}</td>
                    {s.present.map((on, i) => (
                      <td key={dates[i]} className={on ? 'present' : 'absent'}>
                        {on ? 'Present' : '–'}
                      </td>
                    ))}
                    <td className="mono">
                      {s.present.filter(Boolean).length}/{dates.length}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {rows.length === 0 && <div className="muted small">No students match that search.</div>}
        </>
      )}
    </section>
  )
}
