from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import uuid
import shutil
import subprocess
import requests
import json
from pydantic import BaseModel

app = FastAPI(title="Facebook Video Downloader API")

OUTPUT_FOLDER = "downloads"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

class DownloadRequest(BaseModel):
    url: str

def cleanup_file(path: str):
    """Removes the file after it's been sent."""
    if os.path.exists(path):
        os.remove(path)

def extract_fb_video(link: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    try:
        resp = requests.get(link, headers=headers)
        resp.raise_for_status()
    except Exception as e:
        raise Exception(f"Failed to open URL: {str(e)}")

    content = resp.text
    # Simplified logic from app.py to find video_id and links
    # Note: In a production environment, yt-dlp is much more reliable
    try:
        # Try to find video ID from URL
        splits = link.split('/')
        video_id = next((s for s in splits if s.isdigit()), str(uuid.uuid4()))
        
        # This is a placeholder for the logic in app.py
        # For the API, we'll use yt-dlp for better reliability if available
        return video_id
    except:
        return str(uuid.uuid4())

@app.post("/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    video_url = request.url
    job_id = str(uuid.uuid4())
    temp_filename = f"{job_id}.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, temp_filename)

    # Use yt-dlp as it's the gold standard for video downloading
    # and handles merging automatically if ffmpeg is present.
    try:
        cmd = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
            "-o", output_path,
            video_url
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Download failed: {process.stderr}")

        if not os.path.exists(output_path):
            # yt-dlp might have added an extension if not explicitly .mp4
            # but we forced mp4 above. Let's check if it exists.
            raise HTTPException(status_code=500, detail="File was not created.")

        background_tasks.add_task(cleanup_file, output_path)
        
        return FileResponse(
            path=output_path,
            filename=f"fb_video_{job_id}.mp4",
            media_type="video/mp4"
        )

    except Exception as e:
        if "yt-dlp" in str(e):
             raise HTTPException(status_code=500, detail="yt-dlp not found on server.")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Facebook Downloader API is running. Use /docs to see the documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
