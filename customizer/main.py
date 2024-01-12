# PYTHON_ARGCOMPLETE_OK

import argparse
import argcomplete
import inquirer
from rich_argparse import RichHelpFormatter
from alive_progress import alive_bar

import os
import shutil
import toml
import customizer_config

import cv2




def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="bootup-screen-customizer",
        description="""
        CLI to customize bootup-screen and login-screen
        on unix-systems using plymouth.
        """,
        formatter_class=RichHelpFormatter,
    )

    argcomplete.autocomplete(parser)
    
    parser.add_argument("name")
    
    parser.add_argument("--apply",
                        required=False,
                        action="store_false",
                        help="""Shows lists of installed/created themes
                        to the user to select one as next-bootup-theme."""
                        )
    
    parser.add_argument("--framecount",
                        required=False,
                        default=128,
                        type=int,
                        help="""
                        Number of animationframes created
                        when using customized theme.
                        """
                        )
    parser.add_argument("-s", "--sourcepath",
                        required=False,
                        default=os.path.join(os.getcwd(), 'media'),
                        help="""
                        Sourcepath for customized animationsources.
                        """
                        )
    return parser.parse_args()


def create_resultfolder():
    output_folder = os.path.join(os.getcwd(), 'results')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder


def create_theme(name: str):
    theme_dir = os.path.join(customizer_config.PLYMOUTH_DIR, 'themes', name)
    os.mkdir(theme_dir)

    shutil.move(
        src=os.path.join(os.getcwd(), 'results'),
        dest=theme_dir
    )


def apply_theme(name: str):
    # edit /usr/share/plymouth/default.plymouth
    default_path = os.path.join(customizer_config.PLYMOUTH_DIR, 'default.plymouth')
    with open(default_path, 'r') as file:
        data = toml.load(file)

    print(data)

    if 'ImageDir' in data:
        data['ImageDir'] = os.path.join(customizer_config.PLYMOUTH_DIR, 'themes', name)
    else:
        print("Plymouth-config not valid.")

    # update config
    with open(default_path, 'w') as file:
        toml.dump(data, file)


def split_video_into_images(video_path: str, framecount: int = 128):
    output_folder = create_resultfolder()

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, total_frames // framecount)

    with alive_bar(framecount) as bar:
        for i in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()

            if not ret:
                break

            image_path = os.path.join(output_folder, f"animation-{i}.jpg")
            cv2.imwrite(image_path, frame)

            bar()
    # Release the video capture object
    cap.release()


def create_darkened_animation(input_path, theme_name, framecount: int = 128, inverse: bool = False):

    output_folder = create_resultfolder()

    original_image = cv2.imread(input_path)

    # Generate darker versions of source_picture
    with alive_bar(framecount) as bar:
        for i in range(framecount):
            if inverse:
                darkness_factor = i / float(framecount-1)
                print(darkness_factor)
                darkened_image = original_image * (0 + darkness_factor)
                darkened_image = darkened_image.clip(0, 255).astype('uint8')  # pxls within valid rgb-range (0..255)
            else:
                darkness_factor = i / float(framecount-1)
                darkened_image = original_image * (1 - darkness_factor)
                darkened_image = darkened_image.clip(0, 255).astype('uint8')  # pxls within valid rgb-range (0..255)

            output_path = os.path.join(output_folder, f"{theme_name}-{i}.png")
            cv2.imwrite(output_path, darkened_image)

            # update processbar
            bar()


def configure_plymouth_theme(
        name: str = "ubuntu-logosu",
        mode: str = "default"):

    if name:
        input()
    pass


def main(cli_args):
    themes_dir = os.path.join(customizer_config.PLYMOUTH_DIR, 'themes')
    if cli_args.sourcepath == themes_dir:
        # let user select preinstalled themes
        themes = []

        # read available themes from filesystem
        for t in os.listdir(themes_dir):
            if os.path.isdir(os.path.join(themes_dir, t)):
                themes.append(t)

        selection = wait_for_user_selection(
            message="Choose bootup-splash-theme",
            choices=themes
            )

    else:
        os.path.isdir(cli_args.sourcepath)
        mediafiles = []

        # read available mediafiles from filesystem
        for t in os.listdir(cli_args.sourcepath):
            if os.path.isdir(cli_args.sourcepath):
                mediafiles.append(t)

        selection = wait_for_user_selection(
            message="Choose bootup-splash-theme",
            choices=mediafiles
            )

        filetype = validate(os.path.join(cli_args.sourcepath, selection))

        # create animation
        if filetype == "image":

            # ask user for image-animation-mode
            selection = wait_for_user_selection(
                message="Animate given image from",
                choices=["dark to bright", "bright to dark"]
            )

            if selection == "":
                create_darkened_animation(
                    input_path=cli_args.sourcepath,
                    theme_name=cli_args.name,
                    inverse=True
                )

            else:  # bright to dark
                create_darkened_animation(
                    input_path=cli_args.sourcepath,
                    theme_name=cli_args.name,
                )

        elif filetype == "video":
            outputfolder = os.path.join(
                os.getcwd(),
                'results',
                cli_args.name
                )

            split_video_into_images(
                framecount=cli_args.framecount,
                video_path=cli_args.sourcepath,
                )


def validate(file: str):
    print(file)
    assert os.path.isfile(file)
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        return "image"
    elif file.lower().endswith(('.mp4', '.avi', '.mov')):
        return "video"
    else:
        return None


def wait_for_user_selection(message: str, choices: []):
    questions = [
        inquirer.List(
            "var",
            message=message,
            choices=choices,
        ),
    ]
    return inquirer.prompt(questions)["var"]


if __name__ == "__main__":
    main(parse_arguments())
