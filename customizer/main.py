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

    parser.add_argument("name", help="Name of your custom-theme")

    parser.add_argument("-a", "--apply",
                        required=False,
                        action="store_false",
                        help="""Shows lists of installed/created themes
                        to the user to select one as next-bootup-theme."""
                        )
    
    parser.add_argument("-f", "--framecount",
                        required=False,
                        default=64,
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
    
    parser.add_argument("-l", "--login-logo",
                        choices=["no", "default", "custom"],
                        required=False,
                        default="default",
                        help="""
                        Use flag to customize login-logo at the bottom of the screen 
                        CLI will ask you for sourcepath of login-logo
                        
                        - no: no logo.
                        - default: use default logo: /usr/share/plymouth/ubuntu-logo.png
                        - custom: cli will ask you for an additional image-path
                        """)
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


def create_animation_from_video(video_path: str, framecount: int = 128):
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


def create_animation_from_image(
        input_path: str,
        framecount: int = 128,
        mode: str = "light-to-dark"
        ):
    
    output_folder = create_resultfolder()
    original_image = cv2.imread(input_path)

    # Generate darker versions of source_picture
    with alive_bar(framecount) as bar:
        for i in range(framecount):
            darkness_factor = i / float(framecount-1)
            darkened_image = original_image * (1 - darkness_factor)
            darkened_image = darkened_image.clip(0, 255).astype('uint8')  # pxls within valid rgb-range (0..255)

            if mode == "light-to-dark":
                num = i
            else:
                num = framecount - i

            output_path = os.path.join(
                output_folder,
                f"animation-{num}.jpg"
            )
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

        dest_file = os.path.join(cli_args.sourcepath, selection)
        filetype = validate(dest_file)

        # create animation
        if filetype == "image":

            # ask user for image-animation-mode
            selection = wait_for_user_selection(
                message="Animate given image from",
                choices=["light-to-dark", "dark-to-light"]
            )

            create_animation_from_image(
                input_path=dest_file,
                framecount=cli_args.framecount,
                mode=selection
            )

        elif filetype == "video":
            os.path.join(
                os.getcwd(),
                'results',
                cli_args.name
                )

            create_animation_from_video(
                framecount=cli_args.framecount,
                video_path=cli_args.sourcepath,
                )

    if cli_args.login_logo == "no":
        # set var for login-logo in theme-config.toml
        pass
    
    elif cli_args.login_logo == "default":
        check = os.path.exists(
            os.path.join(
                customizer_config.PLYMOUTH_DIR,
                'ubuntu-logo.png'
                )
            )

        if check:
            pass
        else:
            shutil.copyfile(
                src = os.path.join(
                    os.getcwd(),
                    'templates',
                    'ubuntu-logo.png'
                ),
                dst = customizer_config.PLYMOUTH_DIR
            )

        print('Default-logo applied.')

        # set default-logo in <theme>.toml
        # ...
        pass
    
    elif cli_args.login_logo == "custom":

        logofile_path = input("Please provide path for login-logo-image:")

        if os.path.isdir(logofile_path):
            files = os.listdir(path=logofile_path)
            choices = []
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    choices.append(f)
            selected_image = wait_for_user_selection(
                message="Select imagefile for login-logo:",
                choices=choices
            )
            logofile_path = os.path.join(
                logofile_path,
                selected_image
            )
        else:
            logofile_path.lower().endswith(('.png', '.jpg', '.jpeg'))
        
        shutil.copyfile(
            src=logofile_path,
            dst=os.path.join(
                customizer_config.PLYMOUTH_DIR,
                'login-logo.png'
                )
            )


def validate(file: str):
    # print(file)
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
