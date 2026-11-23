const BASE = '/api'

async function readError(response) {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') return body.detail
  } catch {
    // Ignore JSON parse errors
  }
  return `Request failed (${response.status})`
}

export async function uploadVideo(file, lectureDate) {
  const form = new FormData()
  form.append('file', file)
  form.append('lecture_date', lectureDate)

  const response = await fetch(`${BASE}/upload/`, { method: 'POST', body: form })
  if (!response.ok) throw new Error(await readError(response))
  const data = await response.json()
  return data.job_id
}

export async function getJob(jobId) {
  const response = await fetch(`${BASE}/jobs/${jobId}`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getRecords() {
  const response = await fetch(`${BASE}/records`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export const CSV_URL = `${BASE}/attendance.csv`
