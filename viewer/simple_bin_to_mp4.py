# ------------------------------------------------------------------------
# HOLa
# url: https://github.com/mschwimmbeck/HOLa
# Copyright (c) 2023 Michael Schwimmbeck. All Rights Reserved.
# Licensed under the GNU Affero General Public License v3.0 [see LICENSE for details]
# ------------------------------------------------------------------------
# HL2SS 
# url: https://github.com/jdibenes/hl2ss/tree/main
# Copyright (c) 2022 by Stevens Institute of Technology. All Rights Reserved. [see licences for details]
# ------------------------------------------------------------------------

import hl2ss_utilities


filenames_in = [
    './data/personal_video.bin',
    './data/rm_vlc_leftfront.bin',
    './data/microphone.bin'
]

filename_out = './data/video.mp4'

hl2ss_utilities.unpack_to_mp4(filenames_in, filename_out)

