import open3d as o3d
import hl2ss
import hl2ss_3dcv
import numpy as np
from PIL import Image
import os
import re
from glob import glob

###### General settings ######
FullScenePointcloud = True
take = '1'
host = 'X.X.X.X'  # Enter a valid IP address
##############################


def main(take, host):
    save_dir = './hololens_recordings/Take' + take + '/pcd'
    rgb_path = './hololens_recordings/Take' + take + '/rgb'
    depth_path = './hololens_recordings/Take' + take + '/depth'
    pose_path = './hololens_recordings/Take' + take + '/poses'

    calibration_path = './hololens_recordings/Calib'

    rgb_paths = glob(os.path.join(rgb_path, '*.tif'))
    rgb_paths.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])

    depth_paths = glob(os.path.join(depth_path, '*.tif'))
    depth_paths.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])

    pose_paths = glob(os.path.join(pose_path, '*.npy'))
    pose_paths.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])

    # Integration parameters (pointcloud parameter)-------------------------------------------
    voxel_length = 1/100
    sdf_trunc = 0.04
    max_depth = 3
    enable = True

    volume = o3d.pipelines.integration.ScalableTSDFVolume(voxel_length=voxel_length, sdf_trunc=sdf_trunc,
                                                       color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    first_pcd = True

    calibration_lt = hl2ss_3dcv.get_calibration_rm(host, hl2ss.StreamPort.RM_DEPTH_LONGTHROW, calibration_path)
    intrinsics_depth = o3d.camera.PinholeCameraIntrinsic(hl2ss.Parameters_RM_DEPTH_LONGTHROW.WIDTH, hl2ss.Parameters_RM_DEPTH_LONGTHROW.HEIGHT, calibration_lt.intrinsics[0, 0], calibration_lt.intrinsics[1, 1], calibration_lt.intrinsics[2, 0], calibration_lt.intrinsics[2, 1])

    frame = 0

    for (r, d, p) in zip(rgb_paths, depth_paths, pose_paths):
        im = Image.open(r)
        rgb = np.array(im)
        im = Image.open(d)
        depth = np.array(im)
        pose = np.load(p)

        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(o3d.geometry.Image(rgb), o3d.geometry.Image(depth), depth_scale=1, depth_trunc=max_depth, convert_rgb_to_intensity=False)
        depth_world_to_camera = hl2ss_3dcv.world_to_reference(pose) @ hl2ss_3dcv.rignode_to_camera(calibration_lt.extrinsics)

        if not FullScenePointcloud:
            # creating a full point cloud assembled from all frames
            volume.integrate(rgbd, intrinsics_depth, depth_world_to_camera.transpose())
            pcd_tmp = volume.extract_point_cloud()
        else:
            # creating a single point for each frame
            volume_frame = o3d.pipelines.integration.ScalableTSDFVolume(voxel_length=voxel_length, sdf_trunc=sdf_trunc, color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)
            volume_frame.integrate(rgbd, intrinsics_depth, depth_world_to_camera.transpose())
            pcd_tmp = volume_frame.extract_point_cloud()

        o3d.io.write_point_cloud(save_dir + r'\frame_' + str(frame) + '.ply', pcd_tmp)
        frame += 1


main(take, host)
