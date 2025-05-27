import os
import logging
from datetime import datetime
from pathlib import Path

from transcript_utils import get_phrase_timestamps
from clipper import (
    get_latest_video_urls,
    get_video_id,
    download_video,
    download_video_and_clip
)

# Output directory: ~/Downloads/ken-clips
DOWNLOAD_DIR = Path.home() / "Downloads" / "ken-clips"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Config
CHANNEL_URL = "https://www.youtube.com/playlist?list=UUiFOL6V9KbvxfXvzdFSsqCw"  # Ken's uploads playlist
NUM_VIDEOS = 10
PHRASE = "amplification"
BEFORE = 2
AFTER = 2

# Start
if __name__ == "__main__":
    logging.info(f"Fetching latest {NUM_VIDEOS} videos from {CHANNEL_URL}...")

    try:
        video_urls = get_latest_video_urls(CHANNEL_URL, NUM_VIDEOS)
    except Exception as e:
        logging.error(f"Failed to get video URLs: {e}")
        exit(1)

    for url in video_urls:
        try:
            logging.info(f"Processing video: {url}")
            video_id = get_video_id(url)
            full_video_path = DOWNLOAD_DIR / f"{video_id}.mp4"

            # Get timestamps where the phrase appears
            timestamps = get_phrase_timestamps(url, PHRASE)
            if not timestamps:
                logging.info("No matches found for keyword.")
                continue

            logging.info(f"Found {len(timestamps)} timestamp(s): {timestamps}")

            # Download and re-encode full video
            download_video(url, full_video_path)

            # Clip each timestamp
            for i, ts in enumerate(timestamps):
                ts_label = f"{int(ts):03}"
                date_str = datetime.now().strftime("%Y-%m-%d")
                clip_name = DOWNLOAD_DIR / f"kenforrest_{date_str}_{ts_label}_{PHRASE.replace(' ', '-')}.mp4"
                logging.info(f"Clipping segment at {ts:.2f}s → {clip_name.name}")
                download_video_and_clip(url, ts, BEFORE, AFTER, output_filename=clip_name)

            # Delete full video to save space
            os.remove(full_video_path)
            logging.info("Deleted full video to save space.")

        except Exception as e:
            logging.error(f"Failed to process {url}: {e}")
