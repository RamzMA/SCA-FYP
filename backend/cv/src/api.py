"""
   This file is the main api file for the frontend in order to communicate with the backend. 
"""
import shutil
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse

from attendance import CSV_PATH, get_connection
from pipeline import process_video, PROJECT_ROOT

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

app = FastAPI(title="Student Attendance System")

jobs = {}

# Run a job in the background and update the job status in the jobs dictionary.
def run_job(job_id, video_path, lecture_date):
    jobs[job_id]["status"] = "Processing"
    jobs[job_id]["progress"] = 0.0

    def report_progress(fraction):
        jobs[job_id]["progress"] = fraction

    try:
        jobs[job_id]["result"] = process_video(video_path, lecture_date, progress_callback=report_progress)
        jobs[job_id]["status"] = "Done"
    except Exception as e:
        jobs[job_id]['status'] = "Failed"
        jobs[job_id]['error'] = str(e)

#Uploading video endpoint takes in a video file and lecture date, saves the file and starts a background job to process it.
@app.post("/upload/")
def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...), lecture_date: str = Form(...)):
    try:
        # Ensure the lecture date format (YYYY-MM-DD)
        date.fromisoformat(lecture_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format use YYYY-MM-DD.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    #Create a unique job ID and save the uploaded video file to the uploads directory
    job_id = uuid.uuid4().hex
    video_path = UPLOAD_DIR / f"{job_id}{extension}"

    #Upload 64kb chunks at a time to avoid memory issues with large files using pre built function
    with open(video_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    jobs[job_id] = {'status': 'queued'}
    background_tasks.add_task(run_job, job_id, video_path, lecture_date)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/attendance.csv")
def download_csv():
    if not CSV_PATH.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    return FileResponse(CSV_PATH, media_type='text/csv', filename='attendance.csv')


@app.get("/records")
def get_records():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT student_number, student_name, lecture_date FROM attendance"
        ).fetchall()
    finally:
        conn.close()

    dates = sorted({r[2] for r in rows})
    students = {}
    for number, name, lecture_date in rows:
        entry = students.setdefault(number, {"number": number, "name": name, "dates": set()})
        if name and not entry["name"]:
            entry["name"] = name
        entry["dates"].add(lecture_date)

    return {
        "dates": dates,
        "students": [
            {"number": s["number"], "name": s["name"], "present": [d in s["dates"] for d in dates]}
            for s in sorted(students.values(), key=lambda s: s["number"])
        ],
    }

@app.delete("/records")
def clear_records():
    conn = get_connection()
    try:
        conn.execute("DELETE FROM attendance")
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "message": "All records cleared."}
