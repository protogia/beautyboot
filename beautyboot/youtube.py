# dependencies
from pytube import YouTube
from time import time
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import traceback

# custom

YT_DOWNLOAD_PATH = os.path.join(
    os.getcwd(),
    'results',
    'yt'
)


def download(
    url: str,
    start_timestamp: time = None,
    end_timestamp: time = None
):
    yt = YouTube(url)

    stream = yt.streams.get_highest_resolution()
    stream.download(output_path=YT_DOWNLOAD_PATH, filename=yt.title)

    print(f"Downloaded: {yt.title}")

    return yt.length, yt.title, YT_DOWNLOAD_PATH


def cut_video(start_timestamp, end_timestamp, output_path):
    try:
        ffmpeg_extract_subclip(
            output_path,
            start_timestamp,
            end_timestamp,
            targetname=output_path
            )
        return True
    except Exception as e:
        traceback.print_exc(e)
