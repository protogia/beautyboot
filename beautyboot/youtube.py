# dependencies
from pytube import YouTube
import time
from moviepy.editor import VideoFileClip
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
    stream.download(
        output_path=YT_DOWNLOAD_PATH,
        filename=f"{yt.title}.mp4"
    )

    print(f"Downloaded: {yt.title}")

    return yt.length, f"{yt.title}.mp4", YT_DOWNLOAD_PATH


def cut_video(start_timestamp, end_timestamp, output_path):
    t1 = time.strftime("%H:%M:%S", start_timestamp)
    t2 = time.strftime("%H:%M:%S", end_timestamp)
    
    try:
        clip = VideoFileClip(output_path, audio=False)
        clip = clip.subclip(t1, t2)
        clip.write_videofile(output_path)

        return True
    except Exception as e:
        traceback.print_exc(e)
