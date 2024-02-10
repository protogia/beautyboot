# dependencies
from pytube import YouTube
import time
# from moviepy.editor import VideoFileClip
import os
from moviepy.video.io.VideoFileClip import VideoFileClip

# custom

YT_DOWNLOAD_PATH = os.path.join(
    os.getcwd(),
    'results',
    'yt'
)


def get_meta(url: str):
    return YouTube(url)


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
    return True


def cut_video(start_timestamp, end_timestamp, output_filepath):
    t1 = time.strftime("%H:%M:%S", start_timestamp)
    t2 = time.strftime("%H:%M:%S", end_timestamp)

    clip = VideoFileClip(output_filepath, audio=False).subclip(t1, t2)
    clip.write_videofile(output_filepath)

    return True