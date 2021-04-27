# Reference Used:
# https://docs.luxonis.com/projects/api/en/latest/samples/13_encoding_max_limit/?highlight=stream#source-code

import depthai as dai
import os

VIDEO_PATH = "/home/andy/Documents/Autono-Goose/videos/"
MONO_LEFT_FILE = 'mono1.h264'
MONO_RIGHT_FILE = 'mono2.h264'
COLOR_MID_FILE = 'color.h265'

MONO_LEFT_OUTPUT_FILE = 'mono1.mp4'
MONO_RIGHT_OUTPUT_FILE = 'mono2.mp4'
COLOR_MID_OUTPUT_FILE = 'color4k.mp4'

pipeline = dai.Pipeline()

# Nodes
colorCam = pipeline.createColorCamera()
colorCam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
monoCam = pipeline.createMonoCamera()
monoCam2 = pipeline.createMonoCamera()

ve1 = pipeline.createVideoEncoder()
ve2 = pipeline.createVideoEncoder()
ve3 = pipeline.createVideoEncoder()

ve1Out = pipeline.createXLinkOut()
ve2Out = pipeline.createXLinkOut()
ve3Out = pipeline.createXLinkOut()

# Properties
monoCam.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoCam2.setBoardSocket(dai.CameraBoardSocket.RIGHT)
ve1Out.setStreamName('monoLeft')
ve2Out.setStreamName('rgbMid')
ve3Out.setStreamName('monoRight')

# Setup fps to 25
ve1.setDefaultProfilePreset(1280, 720, 25, dai.VideoEncoderProperties.Profile.H264_MAIN)
ve2.setDefaultProfilePreset(3840, 2160, 25, dai.VideoEncoderProperties.Profile.H265_MAIN)
ve3.setDefaultProfilePreset(1280, 720, 25, dai.VideoEncoderProperties.Profile.H264_MAIN)

# Link nodes
monoCam.out.link(ve1.input)
colorCam.video.link(ve2.input)
monoCam2.out.link(ve3.input)

ve1.bitstream.link(ve1Out.input)
ve2.bitstream.link(ve2Out.input)
ve3.bitstream.link(ve3Out.input)

# Connect to device here with the pipeline defined above
with dai.Device(pipeline) as dev:

    # Preparing data queues
    outQ1 = dev.getOutputQueue('monoLeft', maxSize=30, blocking=True)
    outQ2 = dev.getOutputQueue('rgbMid', maxSize=30, blocking=True)
    outQ3 = dev.getOutputQueue('monoRight', maxSize=30, blocking=True)

    # Starting pipeline
    dev.startPipeline()

    # Processing loop
    with open(VIDEO_PATH + MONO_LEFT_FILE, 'wb') as fileMono1H264, open(VIDEO_PATH + COLOR_MID_FILE, 'wb') as fileColorH265, open(VIDEO_PATH + MONO_RIGHT_FILE, 'wb') as fileMono2H264:
        print("Press Ctrl+C to stop recording")
        while True:
            try:
                # empty queues
                while outQ1.has():
                    outQ1.get().getData().tofile(fileMono1H264)

                while outQ2.has():
                    outQ2.get().getData().tofile(fileColorH265)

                while outQ3.has():
                    outQ3.get().getData().tofile(fileMono2H264)

            except KeyboardInterrupt:
                break

    print("Converting from h264/265 to mp4")

    cmd = "ffmpeg -framerate 25 -i {} {}"
    
    os.system(cmd.format(VIDEO_PATH + MONO_LEFT_FILE, VIDEO_PATH + MONO_LEFT_OUTPUT_FILE))
    os.system(cmd.format(VIDEO_PATH + MONO_RIGHT_FILE, VIDEO_PATH + MONO_RIGHT_OUTPUT_FILE))
    os.system(cmd.format(VIDEO_PATH + COLOR_MID_FILE, VIDEO_PATH + COLOR_MID_OUTPUT_FILE))