# ------------------------------------------------------------------------
# HOLa
# url: https://github.com/mschwimmbeck/HOLa
# Copyright (c) 2023 Michael Schwimmbeck. All Rights Reserved.
# Licensed under the GNU Affero General Public License v3.0 [see LICENSE for details]
# ------------------------------------------------------------------------

import cv2
import os
import re


def extract_frame_number(filename):
    match = re.search(r'frame_(\d+)\.tif', filename)
    if match:
        return int(match.group(1))
    return -1


def combine_frames_to_video(frames_directory, output_path, fps):
    frame_files_pre = os.listdir(frames_directory)
    # assure that the file list is sorted with respect to numeric values in the filenames
    frame_files_pre = sorted(frame_files_pre, key=extract_frame_number)
    
    cnt = 0
    frame_files = []

    for element in frame_files_pre:
        frame_files.append(element)

    if not frame_files:
        print("No frames found in the directory.")
        return

    # Read the first frame to get frame size
    first_frame = cv2.imread(os.path.join(frames_directory, frame_files[0]))
    height, width, _ = first_frame.shape

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use appropriate codec
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Combine frames into video
    for frame_file in frame_files:
        frame_path = os.path.join(frames_directory, frame_file)
        frame = cv2.imread(frame_path)

        # Write the frame to the video
        video_writer.write(frame)

    # Release the VideoWriter and close the video file
    video_writer.release()


def main(take):
    # Specify the directory containing the frames
    frames_directory = "./hololens_recordings/Take" + take + "/pv"

    # Specify the output video file path
    output_path = "./assets/frames_take_" + take + ".mp4"

    # Specify the desired frames per second (fps) for the output video
    fps = 30

    # Combine frames into video
    combine_frames_to_video(frames_directory, output_path, fps)
