# dependencies
from pytube import YouTube
import time
import os
import subprocess


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


def cut_video(start_timestamp, end_timestamp, input_filepath):
    t1 = time.strftime("%H:%M:%S", start_timestamp)
    t2 = time.strftime("%H:%M:%S", end_timestamp)

    filename_with_extension = os.path.basename(input_filepath)
    filename, extension = os.path.splitext(filename_with_extension)

    output_filepath = os.path.join(
        os.getcwd(),
        'results',
        'yt',
        f"CUTTED_{filename}.mp4"
    )

    command = [
        'ffmpeg',
        '-ss', t1,
        '-to', t2,
        '-i', input_filepath,
        # '-c', 'copy',
        output_filepath
    ]

    # Run the ffmpeg command
    try:
        subprocess.run(command, check=True)
        print(f"Subclip saved to {output_filepath}")

    except subprocess.CalledProcessError as e:
        print(f"Error cutting video: {e}")

    # delete source
    try:
        os.remove(input_filepath)
        print(f"Source '{input_filepath}' has been deleted successfully.")
    except OSError as e:
        print(f"Error: {e}")

    return output_filepath