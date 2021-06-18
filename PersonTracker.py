#!/usr/bin/env python3

from pathlib import Path
import cv2
import depthai as dai
import numpy as np
import time
import argparse
import math
import time
import serial

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

executing = False
brake = True

labelMap = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

nnPathDefault = str((Path(__file__).parent / Path('models/mobilenet-ssd_openvino_2021.2_6shave.blob')).resolve().absolute())
parser = argparse.ArgumentParser()
parser.add_argument('nnPath', nargs='?', help="Path to mobilenet detection network blob", default=nnPathDefault)
parser.add_argument('-ff', '--full_frame', action="store_true", help="Perform tracking on full RGB frame", default=False)

args = parser.parse_args()

fullFrameTracking = args.full_frame

# Start defining a pipeline
pipeline = dai.Pipeline()

colorCam = pipeline.createColorCamera()
spatialDetectionNetwork = pipeline.createMobileNetSpatialDetectionNetwork()
monoLeft = pipeline.createMonoCamera()
monoRight = pipeline.createMonoCamera()
stereo = pipeline.createStereoDepth()
objectTracker = pipeline.createObjectTracker()

xoutRgb = pipeline.createXLinkOut()
trackerOut = pipeline.createXLinkOut()

xoutRgb.setStreamName("preview")
trackerOut.setStreamName("tracklets")

colorCam.setPreviewSize(300, 300)
colorCam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
colorCam.setInterleaved(False)
colorCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# setting node configs
stereo.setOutputDepth(True)
stereo.setConfidenceThreshold(255)

spatialDetectionNetwork.setBlobPath(args.nnPath)
spatialDetectionNetwork.setConfidenceThreshold(0.9)
spatialDetectionNetwork.input.setBlocking(False)
spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
spatialDetectionNetwork.setDepthLowerThreshold(100)
spatialDetectionNetwork.setDepthUpperThreshold(5000)

# Create outputs
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)

# Link plugins CAM . NN . XLINK
colorCam.preview.link(spatialDetectionNetwork.input)
objectTracker.passthroughTrackerFrame.link(xoutRgb.input)

objectTracker.setDetectionLabelsToTrack([15])  # track only person
# possible tracking types: ZERO_TERM_COLOR_HISTOGRAM, ZERO_TERM_IMAGELESS
objectTracker.setTrackerType(dai.TrackerType.ZERO_TERM_COLOR_HISTOGRAM)
# take the smallest ID when new object is tracked, possible options: SMALLEST_ID, UNIQUE_ID
objectTracker.setTrackerIdAssigmentPolicy(dai.TrackerIdAssigmentPolicy.SMALLEST_ID)

objectTracker.out.link(trackerOut.input)
if fullFrameTracking:
    colorCam.setPreviewKeepAspectRatio(False)
    colorCam.video.link(objectTracker.inputTrackerFrame)
    objectTracker.inputTrackerFrame.setBlocking(False)
    # do not block the pipeline if it's too slow on full frame
    objectTracker.inputTrackerFrame.setQueueSize(2)
else:
    spatialDetectionNetwork.passthrough.link(objectTracker.inputTrackerFrame)

spatialDetectionNetwork.passthrough.link(objectTracker.inputDetectionFrame)
spatialDetectionNetwork.out.link(objectTracker.inputDetections)

stereo.depth.link(spatialDetectionNetwork.inputDepth)

# Pipeline defined, now the device is connected to
with dai.Device(pipeline) as device:

    # Start the pipeline
    device.startPipeline()

    preview = device.getOutputQueue("preview", 4, False)
    tracklets = device.getOutputQueue("tracklets", 4, False)

    startTime = time.monotonic()
    counter = 0
    fps = 0
    seconds = 0
    execTime = 0
    frame = None

    while(True):
        imgFrame = preview.get()
        track = tracklets.get()

        if (counter == 0):
            seconds +=1
        counter+=1
        

        current_time = time.monotonic()
        if (current_time - startTime) > 1 :
            fps = counter / (current_time - startTime)
            counter = 0
            startTime = current_time

        color = (0, 0, 255)
        frame = imgFrame.getCvFrame()
        trackletsData = track.tracklets

        visiblePerson = False

        for t in trackletsData:
            roi = t.roi.denormalize(frame.shape[1], frame.shape[0])
            x1 = int(roi.topLeft().x)
            y1 = int(roi.topLeft().y)
            x2 = int(roi.bottomRight().x)
            y2 = int(roi.bottomRight().y)

            try:
                label = labelMap[t.label]
            except:
                label = t.label
            statusMap = {dai.Tracklet.TrackingStatus.NEW : "NEW", dai.Tracklet.TrackingStatus.TRACKED : "TRACKED", dai.Tracklet.TrackingStatus.LOST : "LOST"}
            cv2.putText(frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
            cv2.putText(frame, f"ID: {[t.id]}", (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
            cv2.putText(frame, statusMap[t.status], (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)
        
            cv2.putText(frame, f"X: {int(t.spatialCoordinates.x)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
            cv2.putText(frame, f"Y: {int(t.spatialCoordinates.y)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
            cv2.putText(frame, f"Z: {int(t.spatialCoordinates.z)} mm", (x1 + 10, y1 + 95), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)

            # print(t.status, t.id, t.spatialCoordinates.x, t.spatialCoordinates.z)
            if t.status == t.TrackingStatus.TRACKED:
                visiblePerson = True
        
        if (len(trackletsData)>0):
            closestPerson = t
            for t in trackletsData:
                if(t.spatialCoordinates.z < closestPerson.spatialCoordinates.z):
                    closestPerson = t

        if visiblePerson == False:
            # ser.write(b's')
            # print(counter, 'stop', 'no person to track')
            if (seconds%4==0 and executing==False and brake==False):
                print(b's', flush=True)   
                ser.write(b's')  
                executing=True
                execTime = seconds+4
                brake = True   

        elif(closestPerson.spatialCoordinates.z <= 2000):
            # print(counter, 'stop', 'too close')
            
            if (executing==False and brake==False):
                print(b's', flush=True)
                ser.write(b's')
                executing=True
                execTime = seconds+4
                brake = True

        else:
            if (executing==False and brake==True and visiblePerson == True) :
                print(closestPerson.spatialCoordinates.z)
                print(b'g', flush=True)
                ser.write(b'g')
                executing=True
                execTime = seconds+4
                brake = False
            # in path check
            inPath = bool( (900-(np.tan(np.deg2rad(5))*t.spatialCoordinates.z)) >0 )                 
            # print(inPath)
            
            
      
                
        cv2.putText(frame, "NN fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)

        frame = cv2.resize(frame, (1000,1000))
        cv2.imshow("tracker", frame)
        if counter == 1:
            print(seconds)
            if (seconds==execTime):
                executing=False
                print('Done executing')

        if cv2.waitKey(1) == ord('q'):
            break
