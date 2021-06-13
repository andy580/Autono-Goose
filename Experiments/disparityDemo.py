from pathlib import Path
import sys
import cv2
import depthai as dai
import numpy as np
from time import monotonic
import time

VIDEO_PATH = "/home/andy/Documents/Autono-Goose/videos/"
mono1Path = "mono1t1.mp4"
mono2Path = "mono2t1.mp4"

stepSize = 0.01

extended_disparity = False
subpixel = False
lr_check = False
outputDepth = True
outputRectified = False

pipeline = dai.Pipeline()

# Sending frames of a video to the depth node instead
left = pipeline.createXLinkIn()
left.setStreamName("inFrameMono1")

right = pipeline.createXLinkIn()
right.setStreamName("inFrameMono2")


# depth map node
stereo = pipeline.createStereoDepth()
stereo.setInputResolution(1280,720)
stereo.setConfidenceThreshold(200)
median = dai.StereoDepthProperties.MedianFilter.KERNEL_7x7
stereo.setMedianFilter(median)
# stereo.setOutputDepth(outputDepth)
stereo.setOutputRectified(outputRectified)
stereo.setLeftRightCheck(lr_check)
stereo.setSubpixel(subpixel)


max_disparity = 95
multiplier = 255 / max_disparity
color = (255,255,255)

# linking camera nodes output to depth nodes input
left.out.link(stereo.left)
right.out.link(stereo.right)

# creating output
xoutDepth = pipeline.createXLinkOut()
xoutDepth.setStreamName("depth")
stereo.disparity.link(xoutDepth.input)

# Creating spatial calculation and input
spatialLocationCalculator = pipeline.createSpatialLocationCalculator()
xoutSpatialData = pipeline.createXLinkOut()
xinSpatialCalcConfig = pipeline.createXLinkIn()
xoutSpatialData.setStreamName('spatialData')
xinSpatialCalcConfig.setStreamName('spatialCalcConfig')

spatialLocationCalculator.passthroughDepth.link(xoutDepth.input)
stereo.depth.link(spatialLocationCalculator.inputDepth)

topLeft = dai.Point2f(0.45,0.45)
bottomRight = dai.Point2f(0.50,0.50)

spatialLocationCalculator.setWaitForConfigInput(False)
config = dai.SpatialLocationCalculatorConfigData()
config.depthThresholds.lowerThreshold = 100
config.depthThresholds.upperThreshold = 10000
config.roi = dai.Rect(topLeft,bottomRight)
spatialLocationCalculator.initialConfig.addROI(config)
spatialLocationCalculator.out.link(xoutSpatialData.input)
xinSpatialCalcConfig.out.link(spatialLocationCalculator.inputConfig)

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


    depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    spatialCalcQueue = device.getOutputQueue(name='spatialData', maxSize=4, blocking=False)    
    spatialCalcConfigInQueue = device.getInputQueue('spatialCalcConfig')

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
        if frameCounter ==0 :
            qIn_Frame_Right.send(imgR)
            qIn_Frame_Right.send(imgR)
        else:
            qIn_Frame_Right.send(imgR)
        # qIn_Frame_Right.send(imgR)
        # qIn_Frame_Right.send(imgR)

        frameCounter +=1
        imgLD = imgL.getCvFrame()
        imgRD = imgR.getCvFrame()

        # cv2.imshow('frameL', imgLD)
        # cv2.imshow('frameR', imgRD)

        inDepth = depthQueue.get()

        inDepthAvg = spatialCalcQueue.get()

        # Copy paste start

        depthFrame = inDepth.getFrame()
        depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
        depthFrameColor = cv2.equalizeHist(depthFrameColor)
        depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_JET)

        

        spatialData = inDepthAvg.getSpatialLocations()
        for depthData in spatialData:
            roi = depthData.config.roi
            roi = roi.denormalize(width=depthFrameColor.shape[1], height=depthFrameColor.shape[0])
            xmin = int(roi.topLeft().x)
            ymin = int(roi.topLeft().y)
            xmax = int(roi.bottomRight().x)
            ymax = int(roi.bottomRight().y)

            fontType = cv2.FONT_HERSHEY_TRIPLEX
            cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)
            cv2.putText(depthFrameColor, f"X: {int(depthData.spatialCoordinates.x)} mm", (xmin + 10, ymin + 20), fontType, 0.5, color)
            cv2.putText(depthFrameColor, f"Y: {int(depthData.spatialCoordinates.y)} mm", (xmin + 10, ymin + 35), fontType, 0.5, color)
            cv2.putText(depthFrameColor, f"Z: {int(depthData.spatialCoordinates.z)} mm", (xmin + 10, ymin + 50), fontType, 0.5, color)


        cv2.imshow("depth", depthFrameColor)

        newConfig = False
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('w'):
            if topLeft.y - stepSize >= 0:
                topLeft.y -= stepSize
                bottomRight.y -= stepSize
                newConfig = True
        elif key == ord('a'):
            if topLeft.x - stepSize >= 0:
                topLeft.x -= stepSize
                bottomRight.x -= stepSize
                newConfig = True
        elif key == ord('s'):
            if bottomRight.y + stepSize <= 1:
                topLeft.y += stepSize
                bottomRight.y += stepSize
                newConfig = True
        elif key == ord('d'):
            if bottomRight.x + stepSize <= 1:
                topLeft.x += stepSize
                bottomRight.x += stepSize
                newConfig = True

        if newConfig:
            config.roi = dai.Rect(topLeft, bottomRight)
            cfg = dai.SpatialLocationCalculatorConfig()
            cfg.addROI(config)
            spatialCalcConfigInQueue.send(cfg)

        # Copy paste end

        # frame = inDepth.getFrame()
        # frame = (frame*multiplier).astype(np.uint8)
        # frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)

        # cv2.imshow("depth",frame)
        time.sleep(0.1)

        if cv2.waitKey(1) == ord('q'):
            break

