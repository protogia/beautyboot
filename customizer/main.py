import argparse
from rich_argparse import RichHelpFormatter
from InquirerPy import inquirer

import os
import cv2


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="ubuntu-bootup-screen-customizer",
        description="CLI to customize ubuntu-bootup-screen and login-screen.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("name")
    parser.add_argument("--theme", required=True, choices=["default", "preinstalled", "customize"], default="default")
    parser.add_argument("--test", required=False, action="store_true", help="Shows bootup-screen-visualisation, after you finished the configuration.")
    
    return parser.parse_args()



def split_video_into_images(video_path, output_folder, num_frames=128):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

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

def configure_plymouth_theme(name: str = "ubuntu-logosu", mode: str = "default"):
    if name:
        input()
    pass

def main():
    args = parse_arguments()
    
    if args.mode == "default":
        # take default-template ubuntu-logosu
        pass
    
    elif args.mode == "preinstalled":
        # let user select preinstalled themes
        
        themes = []
        themes_dir = os.path.join(os.getcwd(),'themes')
        
        # read available themes from filesystem
        for t in  os.listdir(themes_dir):
            if os.path.isdir(os.path.join(themes_dir,t)):
                themes.append(t)

        selection = wait_for_user_selection(message="Choose bootup-splash-theme", choices=themes)        

    elif args.mode == "customize":
        # ask for user-selection: create animation from video vs image
        selection = wait_for_user_selection(message="Choose bootup-splashscreen-theme:", choices=["video", "image"])

        # ask user for filepath & validate            
        file = input("Please provide filepath")
        validate(file, type=selection)

        # create animation
        if selection ==  "image":
            # ask user for image-animation-mode
            # dark-to-light
            # light-to-dark
            pass
        elif selection == "video":
            outputfolder = os.path.join(os.getcwd(), 'results', args.name)
            split_video_into_images(num_frames=256, video_path=file, output_folder=outputfolder)
        
        
def validate(file: str, type: str):
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
    main()