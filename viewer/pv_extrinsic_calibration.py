from scipy.spatial.transform import Rotation
from tqdm import tqdm
import numpy as np
import hl2ss
import hl2ss_3dcv

host = 'X.X.X.X'  # Enter a valid IP address
path = r'./hololens_recordings/Calib'

samples = 32
pv_width = 640
pv_height = 360
pv_framerate = 30
pv_profile = hl2ss.VideoProfile.H264_BASE
pv_bitrate = 2*1024*1024
lf_profile = hl2ss.VideoProfile.H264_BASE
lf_bitrate = 2*1024*1024

client_rc = hl2ss.tx_rc(host, hl2ss.IPCPort.REMOTE_CONFIGURATION)
client_pv = hl2ss.rx_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO,   hl2ss.ChunkSize.PERSONAL_VIDEO, hl2ss.StreamMode.MODE_1, pv_width, pv_height, pv_framerate, pv_profile, pv_bitrate)
client_rn = hl2ss.rx_rm_vlc(host, hl2ss.StreamPort.RM_VLC_LEFTFRONT, hl2ss.ChunkSize.RM_VLC, hl2ss.StreamMode.MODE_1, lf_profile, lf_bitrate)

list_pv = []
list_rn = []

invalid = False

print('Connecting to HL2 (' + host + ')...')

hl2ss.start_subsystem_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO)
client_rc.wait_for_pv_subsystem(True)

client_pv.open()
client_rn.open()

for i in tqdm(range(0, samples)):
    data_pv = client_pv.get_next_packet()
    data_rn = client_rn.get_next_packet()

    invalid = (not hl2ss.is_valid_pose(data_pv.pose)) or (not hl2ss.is_valid_pose(data_rn.pose))
    if invalid:
        break

    list_pv.append(data_pv.pose)
    list_rn.append(data_rn.pose)

client_pv.close()
client_rn.close()

hl2ss.stop_subsystem_pv(host, hl2ss.StreamPort.PERSONAL_VIDEO)
client_rc.wait_for_pv_subsystem(False)

if invalid:
    print('Invalid pose detected')
    print('Please make sure none of the HL2 sensors are covered and try again')
    quit()

list_extrinsics = [rn_pose @ np.linalg.inv(pv_pose) for rn_pose, pv_pose in zip(list_rn, list_pv)]

extrinsics = np.zeros((4, 4), dtype=np.float32)
extrinsics[3, :3] = np.mean(np.array([list_extrinsics[i][3, 0:3] for i in range(0, samples)], dtype=np.float32), axis=0)
extrinsics[:3, :3] = Rotation.from_matrix(np.vstack([list_extrinsics[i][:3, :3].reshape((1, 3, 3)) for i in range(0, samples)])).mean().as_matrix()
extrinsics[3, 3] = 1

hl2ss_3dcv.save_extrinsics_pv(hl2ss.StreamPort.PERSONAL_VIDEO, extrinsics, path)

print('PV extrinsics saved to ' + path)
print('PV extrinsics:')
print(extrinsics)
