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


#------------------------------------------------------------------------------
# Extension: Workaround for the cv2/av imshow issue on some platforms (Ubuntu)
#------------------------------------------------------------------------------
# https://github.com/opencv/opencv/issues/21952
# https://github.com/PyAV-Org/PyAV/issues/978

try:
    cv2.namedWindow('_cv2_21952_av_978_workaround')
    cv2.destroyWindow('_cv2_21952_av_978_workaround')
except:
    pass
