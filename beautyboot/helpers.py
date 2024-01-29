# dependencies
import os
import pathlib
import shutil

# custom
from beautyboot import beautyboot_conf


def create_resultfolder(theme_name: str):
    output_folder = os.path.join(
        os.getcwd(),
        'results',
        theme_name)

    pathlib.Path.mkdir(
        pathlib.Path(output_folder),
        parents=True,
        exist_ok=True
        )

    return output_folder


def create_theme(theme_name: str):
    theme_dir = os.path.join(
        beautyboot_conf.PLYMOUTH_DIR,
        'themes',
        theme_name)

    os.mkdir(theme_dir)

    shutil.move(
        src=os.path.join(
                os.getcwd(),
                'results',
                theme_name
            ),
        dest=theme_dir
    )


def validate(file: str):
    # print(file)
    assert os.path.isfile(file)
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        return "image"
    elif file.lower().endswith(('.mp4', '.avi', '.mov', '.gif')):
        return "video"
    else:
        return None