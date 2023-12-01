# ------------------------------------------------------------------------
# HOLa
# url: https://github.com/mschwimmbeck/HOLa
# Copyright (c) 2023 Michael Schwimmbeck. All Rights Reserved.
# Licensed under the GNU Affero General Public License v3.0 [see LICENSE for details]
# ------------------------------------------------------------------------
# Modified from HL2SS (https://github.com/jdibenes/hl2ss/tree/main)
# Copyright (c) 2022 by Stevens Institute of Technology. All Rights Reserved. [see licences for details]
# ------------------------------------------------------------------------

# We built this code on the hl2ss version 1.0.20.0, but added the following components from version 1.0.22.0:
# - client_umq.py
# - client_vi.py
# Furthermore, due to compatibility issues, we added some functions/classes from other versions to all hl2ss scripts

import os
import sys
sys.path.append(os.path.join(os.getcwd(), "viewer"))

import multiprocessing as mp
import open3d as o3d
import cv2
import hl2ss
import hl2ss_mp
import hl2ss_3dcv
import numpy as np
import concurrent.futures
from tifffile import imwrite

from client_umq import main as send_message
from client_vi import start_command as start_voice_listener
from client_vi import stop_command as stop_voice_listener

active_flag = True


def main(host, take, framerate):

    # General Settings --------------------------------------------------------------------
    # Pointcloud acquisition can be disabled in case of framerate decrease while recording.
    # However, it is possible to generate pointclouds after recording. Please refer to OfflinePointcloudGenerator.py
    create_pointclouds = False
    FullScenePointcloud = False
    # add saving path
    save_dir = './hololens_recordings/Take' + take
    # add sensors calibration path
    calibration_path = './hololens_recordings/Calib'
    # ---------------------------------------------------------------------------------------

    # Camera parameters ---------------------------------------------------------------------
    focus = 1000
    width = 640
    height = 360
    profile = hl2ss.VideoProfile.H265_MAIN
    bitrate = 5*1024*1024
    exposure_mode = hl2ss.PV_ExposureMode.Auto
    exposure = hl2ss.PV_ExposureValue.Max // 4
    iso_speed_mode = hl2ss.PV_IsoSpeedMode.Manual
    iso_speed_value = 1600
    white_balance = hl2ss.PV_ColorTemperaturePreset.Auto
    framerate = int(framerate)

    # Buffer length in seconds----------------------------------------------------------------
    buffer_length = 10
    # -----------------------------------------------------------------------------------------

    # Integration parameters (pointcloud parameter)-------------------------------------------
    voxel_length = 1/100
    sdf_trunc = 0.04
    max_depth = 3
    # -----------------------------------------------------------------------------------------

    # Generate the folders (saving paths) for the RGB-D and pointcloud data-------------------
    os.makedirs(save_dir + r'\rgb', mode=0o777, exist_ok=True)
    os.makedirs(save_dir + r'\depth', mode=0o777, exist_ok=True)
    os.makedirs(save_dir + r'\pcd', mode=0o777, exist_ok=True)
    os.makedirs(save_dir + r'\pv', mode=0o777, exist_ok=True)
    os.makedirs(save_dir + r'\poses', mode=0o777, exist_ok=True)
    # -----------------------------------------------------------------------------------------

    def data_recording():
        # set up HL2SS streaming system
        hl2ss.start_subsystem_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO)

        hl2ss_3dcv.pv_optimize_for_cv(host, focus, exposure_mode, exposure, iso_speed_mode, iso_speed_value, white_balance)

        calibration_pv = hl2ss_3dcv.get_calibration_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO, calibration_path, focus, width, height, framerate, True)
        calibration_lt = hl2ss_3dcv.get_calibration_rm(host, hl2ss.StreamPort.RM_DEPTH_LONGTHROW, calibration_path)
        uv2xy = hl2ss_3dcv.compute_uv2xy(calibration_lt.intrinsics, hl2ss.Parameters_RM_DEPTH_LONGTHROW.WIDTH, hl2ss.Parameters_RM_DEPTH_LONGTHROW.HEIGHT)
        xy1, scale, depth_to_pv_image = hl2ss_3dcv.rm_depth_registration(uv2xy, calibration_lt.scale, calibration_lt.extrinsics, calibration_pv.intrinsics, calibration_pv.extrinsics)

        if create_pointclouds:
            volume = o3d.pipelines.integration.ScalableTSDFVolume(voxel_length=voxel_length, sdf_trunc=sdf_trunc, color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)
            vis = o3d.visualization.Visualizer()
            vis.create_window()
            first_pcd = True

        intrinsics_depth = o3d.camera.PinholeCameraIntrinsic(hl2ss.Parameters_RM_DEPTH_LONGTHROW.WIDTH, hl2ss.Parameters_RM_DEPTH_LONGTHROW.HEIGHT, calibration_lt.intrinsics[0, 0], calibration_lt.intrinsics[1, 1], calibration_lt.intrinsics[2, 0], calibration_lt.intrinsics[2, 1])

        producer = hl2ss_mp.producer()
        producer.configure_pv(True, host, hl2ss.StreamPort.PERSONAL_VIDEO, hl2ss.ChunkSize.PERSONAL_VIDEO, hl2ss.StreamMode.MODE_1, width, height, framerate, profile, bitrate, 'rgb24')
        producer.configure_rm_depth_longthrow(True, host, hl2ss.StreamPort.RM_DEPTH_LONGTHROW, hl2ss.ChunkSize.RM_DEPTH_LONGTHROW, hl2ss.StreamMode.MODE_1, hl2ss.PngFilterMode.Paeth)
        producer.initialize(hl2ss.StreamPort.PERSONAL_VIDEO, framerate * buffer_length)
        producer.initialize(hl2ss.StreamPort.RM_DEPTH_LONGTHROW, hl2ss.Parameters_RM_DEPTH_LONGTHROW.FPS * buffer_length)
        producer.start(hl2ss.StreamPort.PERSONAL_VIDEO)
        producer.start(hl2ss.StreamPort.RM_DEPTH_LONGTHROW)

        manager = mp.Manager()
        consumer = hl2ss_mp.consumer()
        sink_pv = consumer.create_sink(producer, hl2ss.StreamPort.PERSONAL_VIDEO, manager, None)
        sink_depth = consumer.create_sink(producer, hl2ss.StreamPort.RM_DEPTH_LONGTHROW, manager, ...)

        sinks = [sink_pv, sink_depth]
        [sink.get_attach_response() for sink in sinks]

        # wait for the user to start recording with the corresponding voice command
        print("\nReady for recording\nSay 'START' to start recording\nSay 'STOP' to stop recording\n")
        start_voice_listener(host)

        def acquire():
            frame = 0
            try:
                while 1:
                    # acquire and save data of Hololens streams
                    sink_depth.acquire()
                    data_lt = sink_depth.get_most_recent_frame()

                    pose = data_lt.pose
                    np.save(save_dir+r'\poses\frame_' + str(frame) + '.npy', pose)

                    if not hl2ss.is_valid_pose(data_lt.pose):
                        continue
                    _, data_pv = sink_pv.get_nearest(data_lt.timestamp)
                    if (data_pv is None) or (not hl2ss.is_valid_pose(data_pv.pose)):
                        continue

                    depth = hl2ss_3dcv.rm_depth_normalize(data_lt.payload.depth, calibration_lt.undistort_map, scale)
                    depth_to_pv_image = hl2ss_3dcv.camera_to_rignode(calibration_lt.extrinsics) @ hl2ss_3dcv.reference_to_world(data_lt.pose) @ hl2ss_3dcv.world_to_reference(data_pv.pose) @ calibration_pv.intrinsics

                    rgb, depth = hl2ss_3dcv.rm_depth_rgbd_registered(depth, data_pv.payload, xy1, depth_to_pv_image, cv2.INTER_LINEAR)
                    image = np.hstack((hl2ss_3dcv.rm_vlc_to_rgb(depth), rgb/255))  # Depth scaled for visibility
                    cv2.imshow('PV', data_pv.payload)
                    cv2.imshow('RGB-D', image)
                    cv2.waitKey(1)

                    imwrite(save_dir + r'\rgb\frame_' + str(frame) + '.tif', rgb)
                    depth = np.expand_dims(depth, -1)
                    imwrite(save_dir + r'\pv\frame_'+str(frame) + '.tif', data_pv.payload)
                    imwrite(save_dir + r'\depth\frame_' + str(frame) + '.tif', depth)

                    if create_pointclouds:

                        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(o3d.geometry.Image(rgb), o3d.geometry.Image(depth), depth_scale=1, depth_trunc=max_depth, convert_rgb_to_intensity=False)
                        depth_world_to_camera = hl2ss_3dcv.world_to_reference(data_lt.pose) @ hl2ss_3dcv.rignode_to_camera(calibration_lt.extrinsics)

                        if FullScenePointcloud:
                            # creating a full point cloud assembled from all frames
                            volume.integrate(rgbd, intrinsics_depth, depth_world_to_camera.transpose())
                            pcd_tmp = volume.extract_point_cloud()
                        else:
                            # creating a single point for each frame
                            volume_frame = o3d.pipelines.integration.ScalableTSDFVolume(voxel_length=voxel_length, sdf_trunc=sdf_trunc, color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)
                            volume_frame.integrate(rgbd, intrinsics_depth, depth_world_to_camera.transpose())
                            pcd_tmp = volume_frame.extract_point_cloud()

                        if first_pcd:
                            first_pcd = False
                            pcd = pcd_tmp
                            vis.add_geometry(pcd)
                        else:
                            pcd.points = pcd_tmp.points
                            pcd.colors = pcd_tmp.colors
                            vis.update_geometry(pcd)

                        o3d.io.write_point_cloud(save_dir + r'\pcd\frame_' + str(frame) + '.ply', pcd_tmp)

                    # send a signal to the unity app that triggers a function changing the cursor color to red
                    if frame == 0:
                        send_message(host, 'a')

                    frame = frame + 1

                    if create_pointclouds:
                        vis.poll_events()
                        vis.update_renderer()

                    # if the stop voice command was received, cancel data recording
                    global active_flag
                    if not active_flag:
                        # shut down streaming pipeline
                        [sink.detach() for sink in sinks]
                        producer.stop(hl2ss.StreamPort.PERSONAL_VIDEO)
                        producer.stop(hl2ss.StreamPort.RM_DEPTH_LONGTHROW)
                        vis.run()

                        break

            # inform the user that data recording has stopped
            except concurrent.futures._base.CancelledError:
                print("Unexpected error occurred while starting data recording.")

        # check if the user triggers the end of recording with the corresponding voice command
        def abort_acquisition():
            stop_voice_listener(host)
            # send a signal to the unity app that triggers a function changing the cursor color to white again
            send_message(host, 'i')
            return

        # check if a stop signal was received via voice input. If yes, data acquisition is aborted.
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # run data recording and voice input detection in parallel
            future_a = executor.submit(acquire)
            future_b = executor.submit(abort_acquisition)

            # if the stop voice command was received, cancel data recording
            global active_flag
            while active_flag:
                if future_b.done():
                    active_flag = False

    data_recording()
    print("Recording stopped. Data were saved in ./hololens_recordings\n")
