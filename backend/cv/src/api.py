import shutil
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse

from attendance import CSV_PATH
from pipeline import process_video, PROJECT_ROOT

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

app = FastAPI(title="Attendance API")

jobs = {}

def run_job(job_id, video_path, lecture_date):
    jobs[job_id]["status"] = "Processing"
    try:
        jobs[job_id]["result"] = process_video(video_path, lecture_date)
        jobs[job_id]["status"] = "Done"
    except Exception as e:
        jobs[job_id]['status'] = "Failed"
        jobs[job_id]['error'] = str(e)

@app.post("/upload/")
def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...), lecture_date: str = Form(...)):
    try:
        date.fromisoformat(lecture_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex
    video_path = UPLOAD_DIR / f"{job_id}{extension}"

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

