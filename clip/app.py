import os
import logging
import zipfile
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.background import BackgroundTask

from youtube_transcript_api import YouTubeTranscriptApi

from transcript_utils import get_video_id
from clipper import get_latest_video_urls, download_video_and_clip

# Constants
MEDIA_ROOT = Path("media")
CLIPS_ROOT = MEDIA_ROOT / "clips"
VIDEOS_ROOT = MEDIA_ROOT / "videos"
CLIPS_ROOT.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# FastAPI setup
app = FastAPI(title="YouTube Video Clipper API", description="API for clipping YouTube videos based on phrases.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve media directory
app.mount("/clips", StaticFiles(directory=CLIPS_ROOT), name="clips")

# Request/response models
class ClipRequest(BaseModel):
    video_url: str
    phrase: str
    before: int = 2
    after: int = 2

class ClipResponse(BaseModel):
    status: str
    message: str
    clip_urls: Optional[List[str]] = None
    download_all_url: Optional[str] = None

class LatestVideosRequest(BaseModel):
    channel_url: str
    count: int = 10

class LatestVideosResponse(BaseModel):
    status: str
    message: str
    video_urls: List[str]

@app.post("/clip", response_model=ClipResponse)
def clip_video(req: ClipRequest):
    try:
        logging.info(f"Clipping video: {req.video_url} | Phrase: '{req.phrase}'")
        video_id = get_video_id(req.video_url)
        
        # Use cookie authentication if available
        cookie_path = Path("config/cookies.txt")
        if cookie_path.exists():
            ytt_api = YouTubeTranscriptApi(cookie_path=str(cookie_path))
            transcript = ytt_api.fetch(video_id)
        else:
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id)

        # Convert transcript to list of dictionaries
        transcript_list = []
        for entry in transcript:
            transcript_list.append({
                'text': entry.text,
                'start': entry.start,
                'duration': entry.duration
            })

        clip_dir = CLIPS_ROOT / video_id
        clip_dir.mkdir(parents=True, exist_ok=True)

        phrase = req.phrase.lower()
        clip_paths = []
        found = False

        for entry in transcript_list:
            if phrase in entry['text'].lower():
                found = True
                start = entry['start']
                end = start + entry.get('duration', 0)
                clip_start = max(0, start - req.before)
                clip_duration = (end - clip_start) + req.after

                clip_filename = f"clip_{int(start)}.mp4"
                clip_path = clip_dir / clip_filename

                download_video_and_clip(
                    video_url=req.video_url,
                    timestamp=clip_start,
                    before=0,
                    after=clip_duration,
                    output_filename=str(clip_path),
                    cache_dir=str(VIDEOS_ROOT)
                )
                clip_paths.append(clip_path)

        if not found:
            return ClipResponse(status="error", message="No matches found for the phrase.")

        clip_urls = [f"/clips/{video_id}/{path.name}" for path in clip_paths]
        zip_url = f"/download-all/{video_id}"

        return ClipResponse(
            status="success",
            message=f"Created {len(clip_paths)} clip(s).",
            clip_urls=clip_urls,
            download_all_url=zip_url
        )
    except Exception as e:
        logging.error(f"Error during clipping: {e}")
        raise HTTPException(status_code=500, detail="Failed to create clips")

@app.post("/latest-videos", response_model=LatestVideosResponse)
def get_latest_videos(req: LatestVideosRequest):
    try:
        logging.info(f"Fetching latest videos from: {req.channel_url}")
        video_urls = get_latest_video_urls(req.channel_url, req.count)
        return LatestVideosResponse(
            status="success",
            message=f"Fetched {len(video_urls)} videos.",
            video_urls=video_urls
        )
    except Exception as e:
        logging.error(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch latest videos")

@app.get("/download/{video_id}/{filename}")
async def download_clip(video_id: str, filename: str):
    clip_path = CLIPS_ROOT / video_id / filename
    if not clip_path.exists():
        raise HTTPException(status_code=404, detail="Clip not found")

    return FileResponse(
        path=str(clip_path),
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/download-all/{video_id}")
async def download_all_clips(video_id: str):
    clip_dir = CLIPS_ROOT / video_id
    if not clip_dir.exists():
        raise HTTPException(status_code=404, detail="No clips found")

    clip_files = list(clip_dir.glob("*.mp4"))
    if not clip_files:
        raise HTTPException(status_code=404, detail="No clips to download")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"clips_{video_id}_{timestamp}.zip"
    zip_path = CLIPS_ROOT / zip_filename

    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for clip in clip_files:
                zipf.write(clip, arcname=clip.name)

        async def cleanup():
            await asyncio.sleep(5)
            if zip_path.exists():
                zip_path.unlink()
                logging.info(f"Deleted zip file: {zip_path}")

        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
            background=BackgroundTask(cleanup)
        )
    except Exception as e:
        logging.error(f"Failed to create zip file: {e}")
        raise HTTPException(status_code=500, detail="Zip creation failed")
