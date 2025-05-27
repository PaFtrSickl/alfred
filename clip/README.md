# YouTube Video Clipper - Backend

This project is a FastAPI-based backend service for clipping YouTube videos based on spoken phrases found in their transcripts. It supports video downloads, transcript searching, clip generation, and bulk downloads. It’s designed to be paired with a Next.js frontend for a complete SaaS solution.

---

## ✨ Key Features

* ✉️ RESTful API for video clipping based on phrase search
* ▼ Caches full YouTube videos to avoid redundant downloads
* ⌚ Clips segments based on transcript timestamps
* 📁 Supports per-video folders and bulk downloads as ZIP
* ✔️ Clean JSON responses for seamless frontend integration

---

## 📁 Project Structure

```
project/
├── app.py                     # Main FastAPI application
├── clipper.py                 # Video downloading and clipping logic
├── transcript_utils.py        # Transcript parsing and video ID utility
├── requirements.txt           # All Python dependencies
├── media/                     # Root folder for downloaded content
│   ├── videos/                # Cached full video downloads
│   └── clips/                 # Output clips organized by video_id
```

---

## 🌐 API Endpoints

### 1. `POST /clip`

Extracts clips based on transcript matches.

#### Request Body:

```json
{
  "video_url": "https://www.youtube.com/watch?v=abc123",
  "phrase": "example phrase",
  "before": 2,
  "after": 2
}
```

#### Response (success):

```json
{
  "status": "success",
  "message": "Created 3 clip(s).",
  "clip_urls": [
    "/clips/abc123/clip_42.mp4",
    "/clips/abc123/clip_87.mp4"
  ],
  "download_all_url": "/download-all/abc123"
}
```

#### Response (no match):

```json
{
  "status": "error",
  "message": "No matches found for the phrase."
}
```

---

### 2. `POST /latest-videos`

Fetches the latest video URLs from a YouTube channel or playlist.

#### Request Body:

```json
{
  "channel_url": "https://www.youtube.com/@channelname",
  "count": 5
}
```

#### Response:

```json
{
  "status": "success",
  "message": "Fetched 5 videos.",
  "video_urls": [
    "https://www.youtube.com/watch?v=abc123",
    "https://www.youtube.com/watch?v=def456"
  ]
}
```

---

### 3. `GET /download/{video_id}/{filename}`

Download a single clip file.

#### Example:

```
/download/abc123/clip_42.mp4
```

Returns a forced file download in the browser.

---

### 4. `GET /download-all/{video_id}`

Downloads all clips for a given video in a zip file.

* The ZIP file is auto-deleted 5 seconds after download.
* Useful for frontend "Download All" buttons.

#### Example:

```
/download-all/abc123
```

Returns a zip file with:

```
clips_abc123_20250508_152215.zip
```

---

## 💻 Code Breakdown

### `clipper.py`

* **`download_video()`**: Uses `yt_dlp` to download YouTube video. Then uses `ffmpeg-python` to re-encode to MP4 with H.264 + AAC.
* **`clip_segment()`**: Trims segment from full video using ffmpeg based on `start_time` and `duration`.
* **`download_video_and_clip()`**: Manages cache check, video download, and then clips the relevant segment.
* **`get_latest_video_urls()`**: Uses `yt_dlp` to get the most recent video URLs from a playlist or @channel.

### `transcript_utils.py`

* **`get_video_id()`**: Extracts YouTube video ID from full or shortened URLs.
* **`get_phrase_timestamps()`**: Returns list of timestamps where the phrase appears in the transcript.

### `app.py`

* FastAPI app with:

  * CORS configured for local frontend (localhost:5173)
  * Clean logging for API operations
  * Organized clip storage in `/media/clips/{video_id}`
  * API endpoints documented above

---

## 💡 Developer Notes

* The backend **does not depend on a database**. It uses file paths and naming conventions.
* Use the `/clips/...` URLs directly in `<video>` or `<a download>` tags on the frontend.
* `ffmpeg` must be installed on the host system.
* Clip segments are re-encoded for consistent playback.

---

## ✅ Requirements

* Python 3.9+
* `ffmpeg` installed globally (check with `ffmpeg -version`)
* Google-compatible system timezone (for timestamps)

---

## 🧱 Local Setup

```bash
git clone <repo-url>
cd youtube-video-clipper
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

---

## 🌟 Tips for Frontend Integration (Next.js)

* Always show a loading spinner after calling `/clip` — processing takes time
* Store returned `clip_urls` and preview them in `<video controls src=... />`
* Provide a "Download All" button linked to `download_all_url`
* If clip count is zero, show a friendly message
* You can build a search form around the `/latest-videos` endpoint

---

## 📦 Future Improvements

* Auto-cleanup script for old videos & clips
* Support for multiple phrases
* Background task queuing (Celery or RQ)
* Optional DB for user sessions / clip metadata

---

## ✉️ License

MIT or similar - TBD
