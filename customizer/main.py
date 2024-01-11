# PYTHON_ARGCOMPLETE_OK

import argparse
import argcomplete
import inquirer
from rich_argparse import RichHelpFormatter

import os
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
    parser.add_argument("--theme",
                        required=True,
                        choices=[
                            "default",
                            "preinstalled",
                            "customize"
                            ],
                        default="default",
                        )
    parser.add_argument("--test",
                        required=False,
                        action="store_true",
                        help="""Shows bootup-screen-visualisation,
                        after you finished the configuration."""
                        )
    parser.add_argument("--framecount",
                        required=False,
                        default=128,
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
    # Create output folder if it doesn't exist
    output_folder = os.path.join(os.getcwd(), 'results')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


def split_video_into_images(video_path: str, num_frames: int = 256):

    output_folder = create_resultfolder()

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate the frame interval to capture 128 frames
    frame_interval = max(1, total_frames // num_frames)

    # Iterate through frames and save images
    for i in range(0, total_frames, frame_interval):
        # Set the frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)

        # Read the frame
        ret, frame = cap.read()

        if not ret:
            break

        # Save the frame as an image
        image_path = os.path.join(output_folder, f"frame_{i}.png")
        cv2.imwrite(image_path, frame)

    # Release the video capture object
    cap.release()


def create_darkened_animation(input_path, theme_name, inverse: bool = False):

    output_folder = create_resultfolder()

    original_image = cv2.imread(input_path)
    # Generate 256 darkened versions
    for i in range(256):
        if inverse:
            pass

        darkness_factor = i / 255.0

        darkened_image = original_image * (1 - darkness_factor)
        darkened_image = darkened_image.clip(0, 255).astype('uint8')  # Ensure pixel values are within the valid range (0 to 255)

        output_path = os.path.join(output_folder, f"{theme_name}{i}.png")
        cv2.imwrite(output_path, darkened_image)


def configure_plymouth_theme(
        name: str = "ubuntu-logosu",
        mode: str = "default"):

    if name:
        input()
    pass


def main(cli_args):
    if cli_args.theme == "default":
        # take default-template ubuntu-logosu
        pass

    elif cli_args.theme == "preinstalled":
        # let user select preinstalled themes

        themes = []
        themes_dir = os.path.join(os.getcwd(), 'themes')

        # read available themes from filesystem
        for t in os.listdir(themes_dir):
            if os.path.isdir(os.path.join(themes_dir, t)):
                themes.append(t)

        selection = wait_for_user_selection(
            message="Choose bootup-splash-theme",
            choices=themes
            )

    elif cli_args.theme == "customize":
        # ask for user-selection: create animation from video vs image
        selection = wait_for_user_selection(
            message="Choose bootup-splashscreen-theme: ",
            choices=["video", "image"]
            )

        # ask user for found media from --sourcepath-flag
        file = wait_for_user_selection(
            message="Select media-source to create animation: ",
            choices=os.listdir(cli_args.sourcepath)
            )
        validate(file, type=selection)

        # create animation
        if selection == "image":

            # ask user for image-animation-mode
            selection = wait_for_user_selection(
                message="Animate given image from",
                choices=["dark to bright", "bright to dark"]
            )

            if selection == "":
                create_darkened_animation(
                    input_path=file,
                    theme_name=cli_args.name,
                    inverse=True
                )

            else:  # bright to dark
                create_darkened_animation(
                    input_path=file,
                    theme_name=cli_args.name,
                )

        elif selection == "video":
            outputfolder = os.path.join(
                os.getcwd(),
                'results',
                cli_args.name
                )

            split_video_into_images(
                num_frames=256,
                video_path=file,
                output_folder=outputfolder
                )


def validate(file: str, type: str):
    print(file)
    assert os.path.isfile(file)

    if type == "image":
        assert file.lower().endswith(('.png', '.jpg', '.jpeg'))
    elif type == "video":
        assert file.lower().endswith(('.mp4', '.avi', '.mov'))


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
