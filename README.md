# HoloLens Object Labeling (HOLa)
Michael Schwimmbeck, Serouj Khajarian, and Stefanie Remmele (University of Applied Sciences Landshut)

[Paper]() (To be added as soon as availbale)

Video: How to use HOLa
![HOLa - How To Use.mp4](https://github.com/mschwimmbeck/HOLa/blob/main/media/HOLa_-_How_To_Use.mp4)

Network Architecture:
![HOLa - System overview](https://github.com/mschwimmbeck/HOLa/blob/main/media/HOLa_system_overview.png)

## Setup

1) **Install all packages** listed in requirements.txt. All code is based on python 3.9 interpreter.
2) Download SAM model to _./ckpt_. HOLa uses SAM-VIT-H ([sam_vit_h_4b8939.pth](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth)).
3) Download DeAOT/AOT model to _./ckpt_. HOLa uses R50-DeAOT-L ([R50_DeAOTL_PRE_YTB_DAV.pth](https://drive.google.com/file/d/1QoChMkTVxdYZ_eBlZhK2acq9KMQZccPJ/view)).
4) Create a **HoloLens 2 calibration file** with _./viewer/pv_extrinsic_calibration.py_ and save it to _./hololens_recordings/Calib_
5) **Install the HOLa Unity app** (HOLa_1.0.0.0_ARM64.appx) on your HoloLens 2. (Alternatively, you can open _./unity_ in Unity, build the project as app and install the HOLa app on your HoloLens 2 by yourself).
6) Make sure that both computer and HoloLens 2 are **connected to the same Wi-Fi**. Enter your **HoloLens IP address** as "General settings" -> host in _main.py_.
7) Set a **take number** in "General settings" and specify the desired **framerate**. Note that the framerate does not conflict with the hardware properties of the HoloLens.
8) **Run HOLa** on your HoloLens 2.
9) Run **main.py** on your computer and follow the console instructions.

## 1) Recording mode
Recording is based on [HL2SS](https://github.com/jdibenes/hl2ss). Data are acquired in PV, RGB, Depth and Pose format. Pointcloud format is switched off by default as it decreases recording performance. You can either switch on the pointcloud stream in _./viewer/HololensStreaming.py_ or generate pointclouds offline with _./viewer/OfflinePointcloudGenerator.py_.
1) **Adjust the HOLa sphere cursor** onto the object of interest. Make sure to have an appropriate distance from the object such that the object is clearly visible in the initially recorded frame.
2) While keeping the sphere cursor on the object of interest, trigger recording by **saying _"Start"_**. Wait until the cursor color changes to red (indicating active recording). After this, you can move the cursor off the object. 
3) When you wish to stop recording, simply **say _"Stop"_**. The cursor color changes back to white to indicate finalized recording.
4) Find recorded data in _./hololens_recordings_.

## 2) Labeling Mode

Make sure to run this mode on a computer with GPU storage sufficient for running Segment Anything (SAM). 
After the process has finished, you can find all object masks per frame in _./assets_.

### Credits
Licenses for borrowed code can be found in [licenses.md](https://github.com/mschwimmbeck/HOLa/blob/main/licenses.md) file.

* DeAOT/AOT - [https://github.com/yoxu515/aot-benchmark](https://github.com/yoxu515/aot-benchmark)
* SAM - [https://github.com/facebookresearch/segment-anything](https://github.com/facebookresearch/segment-anything)
* SAM-Track - [https://github.com/z-x-yang/Segment-and-Track-Anything](https://github.com/z-x-yang/Segment-and-Track-Anything)
* HL2SS - [https://github.com/jdibenes/hl2ss](https://github.com/jdibenes/hl2ss)

### License
The project is licensed under the [AGPL-3.0 license](https://github.com/mschwimmbeck/HOLa/blob/main/LICENSE.txt). To utilize or further develop this project for commercial purposes through proprietary means, permission must be granted by us (as well as the owners of any borrowed code).

### Citations
Please consider citing the related paper(s) in your publications if it helps your research.
```
TBD: Add paper

@article{cheng2023segment,
  title={Segment and Track Anything},
  author={Cheng, Yangming and Li, Liulei and Xu, Yuanyou and Li, Xiaodi and Yang, Zongxin and Wang, Wenguan and Yang, Yi},
  journal={arXiv preprint arXiv:2305.06558},
  year={2023}
}
@article{kirillov2023segment,
  title={Segment anything},
  author={Kirillov, Alexander and Mintun, Eric and Ravi, Nikhila and Mao, Hanzi and Rolland, Chloe and Gustafson, Laura and Xiao, Tete and Whitehead, Spencer and Berg, Alexander C and Lo, Wan-Yen and others},
  journal={arXiv preprint arXiv:2304.02643},
  year={2023}
}
@inproceedings{yang2022deaot,
  title={Decoupling Features in Hierarchical Propagation for Video Object Segmentation},
  author={Yang, Zongxin and Yang, Yi},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2022}
}
@inproceedings{yang2021aot,
  title={Associating Objects with Transformers for Video Object Segmentation},
  author={Yang, Zongxin and Wei, Yunchao and Yang, Yi},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2021}
}
@article{dibene2022hololens,
  title={HoloLens 2 Sensor Streaming},
  author={Dibene, Juan C and Dunn, Enrique},
  journal={arXiv preprint arXiv:2211.02648},
  year={2022}
}
```
