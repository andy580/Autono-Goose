from pathlib import Path
import sys
import cv2
import depthai as dai
import numpy as np
from time import monotonic
import time

VIDEO_PATH = "/home/andy/Documents/Autono-Goose/videos/"
mono1Path = "mono1t2.mp4"
mono2Path = "mono2t2.mp4"

extended_disparity = False
subpixel = False
lr_check = False

pipeline = dai.Pipeline()

# Sending frames of a video to the depth node instead
left = pipeline.createXLinkIn()
left.setStreamName("inFrameMono1")

right = pipeline.createXLinkIn()
right.setStreamName("inFrameMono2")


# depth map node
depth = pipeline.createStereoDepth()
depth.setInputResolution(1280,720)
depth.setConfidenceThreshold(200)
median = dai.StereoDepthProperties.MedianFilter.KERNEL_7x7
depth.setMedianFilter(median)

max_disparity = 95
multiplier = 255 / max_disparity

# linking camera nodes output to depth nodes input
left.out.link(depth.left)
right.out.link(depth.right)

# creating output
xout = pipeline.createXLinkOut()
xout.setStreamName("disparity")
depth.disparity.link(xout.input)


with dai.Device(pipeline) as device:
    device.startPipeline()


    # defining queues:
    qIn_Frame_Left = device.getInputQueue(name="inFrameMono1", maxSize=4, blocking=False)
    qIn_Frame_Right = device.getInputQueue(name="inFrameMono2", maxSize=4, blocking=False)

    # defining video capture objects
    capL = cv2.VideoCapture(VIDEO_PATH+mono1Path)
    capR = cv2.VideoCapture(VIDEO_PATH+mono2Path)

    def should_run(capL, capR):
        return (capL.isOpened() and capR.isOpened())

    frameL = None
    frameR = None


    q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)
    frameCounter = 0

    while should_run(capL, capR):
        readL_bool, frameL = capL.read()
        readR_bool, frameR = capR.read()

        if not (readL_bool or readR_bool):
            break

        frameL = cv2.cvtColor(frameL, cv2.COLOR_BGR2GRAY)
        frameR = cv2.cvtColor(frameR, cv2.COLOR_BGR2GRAY)

        imgL = dai.ImgFrame()
        imgL.setData(frameL)
        imgL.setTimestamp(monotonic())
        imgL.setInstanceNum(dai.CameraBoardSocket.LEFT)
        imgL.setType(dai.ImgFrame.Type.RAW8)
        imgL.setWidth(1280)
        imgL.setHeight(720)
        if frameCounter == 0:
            qIn_Frame_Left.send(imgL)
            qIn_Frame_Left.send(imgL)
        else:
            qIn_Frame_Left.send(imgL)

        imgR = dai.ImgFrame()
        imgR.setData(frameR)
        imgR.setTimestamp(monotonic())
        imgR.setInstanceNum(dai.CameraBoardSocket.RIGHT)
        imgR.setType(dai.ImgFrame.Type.RAW8)
        imgR.setWidth(1280)
        imgR.setHeight(720)
        if frameCounter == 0:
            qIn_Frame_Right.send(imgR)
            qIn_Frame_Right.send(imgR)
        else:
            qIn_Frame_Right.send(imgR)

        frameCounter +=1
        imgLD = imgL.getCvFrame()
        imgRD = imgR.getCvFrame()

        cv2.imshow('frameL', imgLD)
        cv2.imshow('frameR', imgRD)

        inDepth = q.get()
        frame = inDepth.getFrame()
        frame = (frame*multiplier).astype(np.uint8)
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)

        cv2.imshow("disparity",frame)
        # time.sleep(0.01)

        if cv2.waitKey(1) == ord('q'):
            break

