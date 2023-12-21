# ------------------------------------------------------------------------
# HOLa
# url: https://github.com/mschwimmbeck/HOLa
# Copyright (c) 2023 Michael Schwimmbeck. All Rights Reserved.
# Licensed under the GNU Affero General Public License v3.0 [see LICENSE for details]
# ------------------------------------------------------------------------

from viewer.HololensStreaming import main as hololens_streaming
from SAMTrack import main as sam_track
from frames2video import main as preprocess_frames


###### General settings ######
# 1) Enter the HoloLens 2 IP address
host = 'X.X.X.X'
# 2) Set the number of the recorded take e.g., '1' for Take1
take = '1'
# 3) You can set a custom seedpoint for labeling mode. For using HOLa in default mode, set custom_seedpoint to None.
custom_seedpoint = None
##############################


def main():
    def recording_mode():
        # start recording mode
        hololens_streaming(host, take)

    def labeling_mode():
        # start labeling mode
        # 1) glue all recorded frames to a video
        # 2) hand the video to SAM-Track that tracks the object of interest throughout all frames and saves the labels
        preprocess_frames(take)
        sam_track(take, custom_seedpoint)

    while True:
        # Create console main menu
        # 1) Start recording mode
        # 2) Start labeling mode
        # q) Quit program

        user_input = input("HOLa MENU\n(1) Recording Mode\n(2) Labeling Mode\nEnter 'q' to quit\n")

        if user_input.lower() == '1':
            recording_mode()
        elif user_input.lower() == '2':
            labeling_mode()
        elif user_input.lower() == 'q':
            print("\nExiting the program.")
            break
        else:
            print("Invalid input. Please try again.\n")


if __name__ == "__main__":
    main()
