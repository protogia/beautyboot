# PYTHON_ARGCOMPLETE_OK

# dependencies
import argparse
import argcomplete
import inquirer
from rich_argparse import RichHelpFormatter
from alive_progress import alive_bar
import os
import shutil
import readline
import toml
import cv2

# custom
from beautyboot import beautyboot_conf
import helpers


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

    parser.add_argument("name",
                        help="Name of your custom-theme"
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

    parser.add_argument("-l", "--with-login-logo",
                        required=False,
                        action="store_true",
                        help="""
                        Use flag to add a custom login-logo
                        at the bottom of the screen
                        CLI will ask you for sourcepath of login-logo.
                        """)

    parser.add_argument("-a", "--apply",
                        required=False,
                        action="store_true",
                        help="""
                        [SUDO-PERMISSIONS NEEDED]:

                        Makes the provided/created theme
                        the default next-bootup-theme.
                        """
                        )

    return parser.parse_args()


def apply_theme(name: str, theme_name: str):
    templates_path = os.path.join(
        os.getcwd(),
        'templates'
    )

    # apply login-logo
    if "login-logo.png" in os.listdir(templates_path):
        src = os.path.join(
            templates_path,
            beautyboot_conf.PLYMOUTH_DEF_LOGINLOGO
            )
        dst = os.path.join(
            beautyboot_conf.PLYMOUTH_DIR,
            beautyboot_conf.PLYMOUTH_DEF_LOGINLOGO
            )
        shutil.move(
            src,
            dst
        )
        print("Install login-logo.png")

    # apply templates
    for template in os.listdir(templates_path):
        src = os.path.join(templates_path, template)

        if "template" in template:
            template = template.replace("template", theme_name)

        dst = os.path.join(
            beautyboot_conf.PLYMOUTH_DIR,
            'themes',
            theme_name,
            template
            )

        shutil.copy(
            src,
            dst)

        print(f"Apply {template}")

    # edit /usr/share/plymouth/default.plymouth
    default_path = os.path.join(
        beautyboot_conf.PLYMOUTH_DIR,
        'themes',
        beautyboot_conf.PLYMOUTH_CONFIG)

    with open(default_path, 'r') as file:
        config_vars = toml.dump(default_path, file)

    config_vars["Name"] = theme_name
    config_vars["Description"] = input("Provide a short theme-description")
    config_vars["ImageDir"] = os.path.join(
        beautyboot_conf.PLYMOUTH_DIR,
        'themes',
        theme_name
        )


def create_animation_from_video(
        video_path: str,
        theme_name: str,
        framecount: int = 128
        ):

    output_folder = helpers.create_resultfolder(theme_name)

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, total_frames // framecount)
    counter = 0
    with alive_bar(framecount) as bar:
        for i in range(0, total_frames, frame_interval):

            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()

            if not ret:
                break

            image_path = os.path.join(
                output_folder,
                f"animation-{counter}.jpg")
            cv2.imwrite(image_path, frame)

            # progress
            counter += 1
            bar()

    # Release the video capture object
    cap.release()


def create_animation_from_image(
        input_path: str,
        theme_name: str,
        framecount: int = 128,
        mode: str = "light-to-dark"
        ):

    output_folder = helpers.create_resultfolder(theme_name)
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
    themes_dir = os.path.join(beautyboot_conf.PLYMOUTH_DIR, 'themes')
    if cli_args.sourcepath == themes_dir:
        # let user select preinstalled themes

        # read available themes from filesystem
        themes = []
        for t in os.listdir(themes_dir):
            if os.path.isdir(os.path.join(themes_dir, t)):
                themes.append(t)

        selection = wait_for_user_selection(
            message="Choose bootup-splash-theme",
            choices=themes
            )

    else:
        if os.path.isdir(cli_args.sourcepath):
            mediafiles = []

            # read available mediafiles from filesystem
            for t in os.listdir(cli_args.sourcepath):
                if helpers.validate(t) is not None:
                    mediafiles.append(t)

            selection = wait_for_user_selection(
                message="Choose bootup-splash-theme",
                choices=mediafiles
                )

            dest_file = os.path.join(cli_args.sourcepath, selection)
        else:
            dest_file = cli_args.sourcepath

        # create animation
        filetype = helpers.validate(dest_file)
        if filetype == "image":

            selection = wait_for_user_selection(
                message="Animate given image from",
                choices=["light-to-dark", "dark-to-light"]
            )

            create_animation_from_image(
                input_path=dest_file,
                theme_name=cli_args.name,
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
                theme_name=cli_args.name,
                video_path=cli_args.sourcepath,
                )

        else:
            print("""
                  Please select a valid filetype.
                  Use [.png, .jpg] for animation from images
                  or [.mp4, .avi, .mov] for animation from videos.
                  """
                  )

    if cli_args.with_login_logo:
        logofile_path = read_userinput_with_autocompletion(
            prompt="Please provide path for login-logo-image:"
        )

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

        resized = resize_image(
            logofile_path,
            width=beautyboot_conf.PLYMOUTH_DEF_LOGINLOGO_WIDTH,
            height=beautyboot_conf.PLYMOUTH_DEF_LOGINLOGO_HEIGHT
            )

        dst = os.path.join(
                os.getcwd(),
                'results',
                cli_args.name,
                beautyboot_conf.PLYMOUTH_DEF_LOGINLOGO
                )

        check = cv2.imwrite(dst, resized)
        if check:
            print("Successfully created login-logo.")
        else:
            print("Failed to create login-logo.")


def wait_for_user_selection(message: str, choices: []):
    questions = [
        inquirer.List(
            "var",
            message=message,
            choices=choices,
        ),
    ]
    return inquirer.prompt(questions)["var"]


def read_userinput_with_autocompletion(prompt):
    readline.set_completer_delims(' \t\n')
    readline.parse_and_bind("tab: complete")
    print(prompt)
    user_input = input()
    user_input = os.path.expanduser(user_input)
    return user_input


def resize_image(imagepath: str, width: int, height: int):
    original = cv2.imread(imagepath, cv2.IMREAD_UNCHANGED)
    resized = cv2.resize(original, dsize=(width, height))
    print(f"Image resized to default-size: ({width}px,{height}px).")
    return resized


if __name__ == "__main__":
    main(parse_arguments())
