# ------------------------------------------------------------------------
# HOLa
# url: https://github.com/mschwimmbeck/HOLa
# Copyright (c) 2023 Michael Schwimmbeck. All Rights Reserved.
# Licensed under the GNU Affero General Public License v3.0 [see LICENSE for details]
# ------------------------------------------------------------------------
# Modified from Segment Anything (https://github.com/facebookresearch/segment-anything)
# Copyright (c) 2023 Meta AI Research, FAIR. All Rights Reserved.
# Licensed under the Apache License 2.0 [see licences for details]
# ------------------------------------------------------------------------
# Modified from SAM-Track (https://github.com/z-x-yang/Segment-and-Track-Anything)
# Copyright (c) 2023 Yangming Cheng et al., College of Computer Science and Technology, Zhejiang University. All Rights Reserved.
# Licensed under the GNU Affero General Public License v3.0 [see licences for details]
# ------------------------------------------------------------------------

import os
import cv2
from SegTracker import SegTracker
from model_args import aot_args
from PIL import Image
from aot_tracker import _palette
import numpy as np
import torch
import matplotlib.pyplot as plt
from scipy.ndimage import binary_dilation
import gc


def save_prediction(pred_mask, output_dir, file_name):
    save_mask = Image.fromarray(pred_mask.astype(np.uint8))
    save_mask = save_mask.convert(mode='P')
    save_mask.putpalette(_palette)
    save_mask.save(os.path.join(output_dir, file_name))


def colorize_mask(pred_mask):
    save_mask = Image.fromarray(pred_mask.astype(np.uint8))
    save_mask = save_mask.convert(mode='P')
    save_mask.putpalette(_palette)
    save_mask = save_mask.convert(mode='RGB')
    return np.array(save_mask)


def draw_mask(img, mask, alpha=0.5, id_countour=False):
    img_mask = np.zeros_like(img)
    img_mask = img
    if id_countour:
        # very slow ~ 1s per image
        obj_ids = np.unique(mask)
        obj_ids = obj_ids[obj_ids != 0]

        for id in obj_ids:
            # Overlay color on  binary mask
            if id <= 255:
                color = _palette[id * 3:id * 3 + 3]
            else:
                color = [0, 0, 0]
            foreground = img * (1 - alpha) + np.ones_like(img) * alpha * np.array(color)
            binary_mask = (mask == id)

            # Compose image
            img_mask[binary_mask] = foreground[binary_mask]

            countours = binary_dilation(binary_mask, iterations=1) ^ binary_mask
            img_mask[countours, :] = 0
    else:
        binary_mask = (mask != 0)
        countours = binary_dilation(binary_mask, iterations=1) ^ binary_mask
        foreground = img * (1 - alpha) + colorize_mask(mask) * alpha
        img_mask[binary_mask] = foreground[binary_mask]
        img_mask[countours, :] = 0

    return img_mask.astype(img.dtype)


def sam_seedpoint_prompt(frame, custom_seedpoint):
    # by default, the seedpoint is set to the frame's center as the sphere cursor simulates this point in HOLa app
    # if you change the frame size, the seedpoint has to be set to the frame's center again
    if not custom_seedpoint:
        seedpoint = (320, 180)
    else:
        seedpoint = custom_seedpoint
        print("Selected custom seedpoint!")

    from segment_anything import sam_model_registry, SamPredictor

    # in contrast to SAM-Track, HOLa uses the SAM vit-h model instead of the SAM vit_b model
    sam_checkpoint = r"./ckpt/sam_vit_h_4b8939.pth"
    model_type = "vit_h"

    device = "cuda"

    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)

    predictor = SamPredictor(sam)
    predictor.set_image(frame)

    # set frame center as SAM seedpoint
    input_point = np.asarray(([seedpoint]))
    input_label = np.array([1])

    # predict three masks
    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )

    # select the mask with the highest IoU prediction
    pre_score = [scores]
    best_mask = masks[np.argmax(pre_score)]

    return best_mask


def main(take, custom_seedpoint):
    # set up file names
    video_name = 'frames_take_' + take
    io_args = {
        'input_video': f'./assets/{video_name}.mp4',
        'output_mask_dir': f'./assets/{video_name}_masks',  # save pred masks
        'output_masked_frame_dir': f'./assets/{video_name}_masked_frames',  # save frames with pred mask overlay
        'output_video': f'./assets/{video_name}_seg.mp4',  # mask+frame vizualization, mp4 or avi, else the same as input video
        'output_gif': f'./assets/{video_name}_seg.gif',  # mask visualization
    }

    # For every sam_gap frames, we use SAM to find new objects and add them for tracking
    # larger sam_gap is faster but may not spot new objects in time
    segtracker_args = {
        'sam_gap': 5,  # the interval to run sam to segment new objects
        'min_area': 200,  # minimal mask area to add a new mask as a new object
        # 'max_obj_num': 255, # maximal object number to track in a video
        'max_obj_num': 1,  # maximal object number to track in a video
        'min_new_obj_iou': 0.8,  # the area of a new object in the background should > 80%
    }

    # initialize SAM-Track by an initial seedpoint-prompt-generated mask of the object of interest
    cap = cv2.VideoCapture(io_args['input_video'])
    frame_idx = 0
    segtracker = SegTracker(segtracker_args, aot_args)
    segtracker.restart_tracker()
    with torch.cuda.amp.autocast():
        while cap.isOpened():
            ret, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pred_mask = sam_seedpoint_prompt(frame, custom_seedpoint)
            torch.cuda.empty_cache()
            obj_ids = np.unique(pred_mask)
            obj_ids = obj_ids[obj_ids != 0]
            break
        cap.release()
        init_res = draw_mask(frame, pred_mask, id_countour=False)
        plt.figure(figsize=(10, 10))
        plt.axis('off')
        plt.imshow(init_res)
        # plt.show()
        plt.figure(figsize=(10, 10))
        plt.axis('off')
        plt.imshow(colorize_mask(pred_mask))
        # plt.show()

        del segtracker
        torch.cuda.empty_cache()
        gc.collect()

    # source video to segment
    cap = cv2.VideoCapture(io_args['input_video'])
    fps = cap.get(cv2.CAP_PROP_FPS)
    # output masks
    output_dir = io_args['output_mask_dir']
    overlay_output_dir = io_args['output_masked_frame_dir']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(overlay_output_dir):
        os.makedirs(overlay_output_dir)
    pred_list = []

    torch.cuda.empty_cache()
    gc.collect()

    # track the initially generated mask throughout the video
    frame_idx = 0
    segtracker = SegTracker(segtracker_args, aot_args)
    segtracker.restart_tracker()

    with torch.cuda.amp.autocast():
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if frame_idx == 0:
                pred_mask = sam_seedpoint_prompt(frame, custom_seedpoint)
                torch.cuda.empty_cache()
                gc.collect()
                segtracker.add_reference(frame, pred_mask)
            else:
                pred_mask = segtracker.track(frame, update_memory=True)

            torch.cuda.empty_cache()
            gc.collect()
            save_prediction(pred_mask, output_dir, str(frame_idx) + '.png')
            colorized_pred_mask = draw_mask(frame, pred_mask, id_countour=False)
            cv2.imwrite(overlay_output_dir + '/' + str(frame_idx) + '.png', cv2.cvtColor(colorized_pred_mask, cv2.COLOR_BGR2RGB))

            pred_list.append(pred_mask)
            frame_idx += 1
        cap.release()

    # draw the predicted mask on frame and save as a video
    cap = cv2.VideoCapture(io_args['input_video'])
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if io_args['input_video'][-3:] == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    elif io_args['input_video'][-3:] == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    else:
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    out = cv2.VideoWriter(io_args['output_video'], fourcc, fps, (width, height))

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pred_mask = pred_list[frame_idx]
        masked_frame = draw_mask(frame, pred_mask)
        masked_frame = cv2.cvtColor(masked_frame, cv2.COLOR_RGB2BGR)
        out.write(masked_frame)
        frame_idx += 1
    out.release()
    cap.release()
    print('Postprocessing finished. Results were saved in ./assets\n')

    # manually release memory (after cuda out of memory)
    del segtracker
    torch.cuda.empty_cache()
    gc.collect()
