import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import yt_dlp
import ffmpeg  # type: ignore

from transcript_utils import get_video_id


def download_video(video_url: str, output_path: str):
    """Downloads a YouTube video and re-encodes it using ffmpeg-python for compatibility."""
    output_path = Path(output_path)
    raw_path = output_path.with_name(output_path.stem + "_raw.mp4")

    # Step 1: Download raw file
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=1080][fps<=60]+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp4',
        'outtmpl': str(raw_path),
        'quiet': True,
        'format_sort': ['res:1080', 'fps:60'],
        'nopart': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    logging.info(f"Downloaded video to {raw_path}, now re-encoding with ffmpeg-python...")

    # Step 2: Re-encode using ffmpeg-python
    try:
        (
            ffmpeg
            .input(str(raw_path))
            .output(
                str(output_path),
                vcodec='libx264',
                acodec='aac',
                audio_bitrate='192k',
                preset='ultrafast'
            )
            .overwrite_output()
            .run(quiet=True)
        )
        logging.info(f"Re-encoded and saved to: {output_path}")
    except ffmpeg.Error as e:
        logging.error(f"ffmpeg-python failed: {e.stderr.decode() if hasattr(e, 'stderr') else e}")

    raw_path.unlink(missing_ok=True)


def clip_segment(input_path: str, start_time: float = 0, duration: float = None, output_path: str = "output.mp4"):
    """Clips or re-encodes a video segment using ffmpeg-python."""
    try:
        stream = ffmpeg.input(input_path, ss=start_time)
        stream = ffmpeg.output(
            stream,
            output_path,
            t=duration if duration is not None else None,
            vcodec='libx264',
            acodec='aac',
            audio_bitrate='192k',
            preset='ultrafast'
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        logging.info(f"Saved clip: {output_path}")
    except ffmpeg.Error as e:
        logging.error(f"ffmpeg-python failed while creating clip: {e.stderr.decode() if hasattr(e, 'stderr') else e}")


def download_video_and_clip(video_url: str, timestamp: float, before: int = 10, after: int = 5,
                            output_filename: str = "clip.mp4", cache_dir: str = "cache"):
    """Downloads (if needed) and clips a segment around the timestamp."""
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    video_id = get_video_id(video_url)
    full_video_path = Path(cache_dir) / f"{video_id}.mp4"

    if not full_video_path.exists():
        logging.info(f"Downloading and preparing full video for {video_id}")
        download_video(video_url, str(full_video_path))

    clip_start = max(0, timestamp - before)
    duration = before + after
    clip_segment(str(full_video_path), start_time=clip_start, duration=duration, output_path=output_filename)


def get_latest_video_urls(channel_url: str, count: int = 10) -> list[str]:
    """Fetches latest video URLs from a channel or playlist."""
    urls = []

    try:
        logging.info("Resolving channel or playlist URL...")
        if "@" in channel_url:
            info = yt_dlp.YoutubeDL({'quiet': True}).extract_info(channel_url, download=False)
            channel_id = info['id']
            playlist_url = f"https://www.youtube.com/playlist?list=UU{channel_id[2:]}"
            logging.info(f"Resolved @channel to playlist: {playlist_url}")
        else:
            playlist_url = channel_url

        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'playlistend': count
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

        if not info.get('entries'):
            logging.warning("No entries found.")
            return []

        for entry in info['entries']:
            urls.append(f"https://www.youtube.com/watch?v={entry['id']}")

        logging.info(f"Fetched {len(urls)} video URLs.")
        return urls

    except Exception as e:
        logging.error(f"Error fetching latest videos: {e}")
        raise
