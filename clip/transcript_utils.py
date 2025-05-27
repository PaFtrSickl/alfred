from typing import List
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import logging
from pathlib import Path


def get_video_id(url: str) -> str:
    """Extracts the YouTube video ID from a full or shortened URL."""
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname and 'youtube.com' in parsed_url.hostname:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    raise ValueError("Invalid YouTube URL")


def get_phrase_timestamps(video_url: str, phrase: str) -> List[float]:
    """
    Returns a list of timestamps (in seconds) where the phrase occurs in the video's transcript.

    Parameters:
        video_url: full YouTube video URL
        phrase: phrase to search for (case-insensitive)

    Returns:
        List of float timestamps, or empty list if not found or transcript unavailable
    """
    video_id = get_video_id(video_url)
    cookie_path = Path("config/cookies.txt")

    try:
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

    except TranscriptsDisabled:
        logging.warning(f"Transcripts are disabled for video: {video_url}")
        return []
    except NoTranscriptFound:
        logging.warning(f"No transcript found for video: {video_url}")
        return []
    except Exception as e:
        logging.error(f"Failed to fetch transcript for {video_url}: {e}")
        return []

    phrase = phrase.lower()
    return [entry['start'] for entry in transcript_list if phrase in entry['text'].lower()]
