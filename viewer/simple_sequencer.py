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

import cv2
import hl2ss
import hl2ss_io

rd_pv = hl2ss_io.create_rd(True, './data/personal_video.bin', hl2ss.ChunkSize.SINGLE_TRANSFER, 'bgr24')
rd_vlc = hl2ss_io.sequencer(True, './data/rm_vlc_leftfront.bin', hl2ss.ChunkSize.SINGLE_TRANSFER, None)

rd_pv.open()
rd_vlc.open()

while (True):
    data_pv = rd_pv.read()
    if (data_pv is None):
        break
    data_vlc = rd_vlc.read(data_pv.timestamp)
    if (data_vlc is not None):
        cv2.imshow('vlc', data_vlc.payload)
    cv2.imshow('pv', data_pv.payload.image)
    cv2.waitKey(1)

rd_pv.close()
rd_vlc.close()
