#!/usr/bin/env python3

from pathlib import Path
import cv2
import depthai as dai
import numpy as np
import time
import argparse
from time import monotonic

VIDEO_PATH = "/home/andy/Documents/Autono-Goose/videos/"
mono1Path = "mono1t2.mp4"
mono2Path = "mono2t2.mp4"
rgbPath = 'color4kt2.mp4'

# nnPath    = str((Path(__file__).parent / Path('./models/OpenVINO_2021_2/mobilenet-ssd_openvino_2021.2_6shave.blob')).resolve().absolute())
nnPath = '/home/andy/Documents/Autono-Goose/models/road-segmentation-adas-0001-8shaves.blob'
# videoPath = str((Path(__file__).parent / Path('./Street_Scenes.mp4')).resolve().absolute())
videoPath = VIDEO_PATH + rgbPath

# MobilenetSSD label texts
labelMap = ["BG", "road", "curbs", "marks"]
yellowF = np.zeros((512,896,3), np.uint8)
yellowF[:,:,0:2] = 255
blueF = np.zeros((512,896,3), np.uint8)
blueF[:,:,0] = 255
greenF = np.zeros((512,896,3), np.uint8)
greenF[:,:,1] = 255
redF = np.zeros((512,896,3), np.uint8)
redF[:,:,2] = 255


parser = argparse.ArgumentParser()
parser.add_argument('-cam', '--camera', action="store_true", help="Use DepthAI 4K RGB camera for inference (conflicts with -vid)")
parser.add_argument('-vid', '--video', type=str, help="Path to video file to be used for inference (conflicts with -cam)", default=videoPath)
args = parser.parse_args()

# Start defining a pipeline
pipeline = dai.Pipeline()

# Define a neural network that will make predictions based on the source frames
# DetectionNetwork class produces ImgDetections message that carries parsed
# detection results.
nn = pipeline.createNeuralNetwork()
nn.setBlobPath(nnPath)
nn.input.setBlocking(False)

# Define a source for the neural network input
# Create XLinkIn object as conduit for sending input video file frames
# to the neural network
xinFrame = pipeline.createXLinkIn()
xinFrame.setStreamName("inFrame")
# Connect (link) the video stream from the input queue to the
# neural network input
xinFrame.out.link(nn.input)

# Create neural network output (inference) stream
nnOut = pipeline.createXLinkOut()
nnOut.setStreamName("nn")
nn.out.link(nnOut.input)

# Pipeline defined, now the device is connected to
with dai.Device(pipeline) as device:

    # Start pipeline
    device.startPipeline()

    # Define queues for image frames
        # Input queue for sending video frames to device
    qIn_Frame = device.getInputQueue(name="inFrame", maxSize=1, blocking=False)
    
    qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

    cap = cv2.VideoCapture(videoPath)

    def should_run():
        return cap.isOpened()

    def get_frame():
        return cap.read()

    startTime = time.monotonic()
    counter = 0
    detections = []
    frame = None

    def to_planar(arr: np.ndarray, shape: tuple) -> np.ndarray:
            return cv2.resize(arr, shape).transpose(2, 0, 1).flatten()

    def displayFrame(name, frame):
        frame = cv2.resize(frame,(896,512))
        cv2.imshow(name, frame)

    fcounter = 0
    while should_run():
        # Get image frames from camera or video file
        read_correctly, frame = get_frame()
        fcounter += 1
        if not read_correctly:
            break

        # Prepare image frame from video for sending to device
        img = dai.ImgFrame()
        img.setData(to_planar(frame, (896, 512)))
        img.setTimestamp(monotonic())
        img.setWidth(896)
        img.setHeight(512)
        # Use input queue to send video frame to device
        qIn_Frame.send(img)

        inDet = qDet.tryGet()
        if inDet is not None:

            shape = (4, 512, 896)
            frame2 = np.array(inDet.getFirstLayerFp16()).reshape(shape)
            
            overlayB = np.zeros((512,896,3), np.uint8)
            overlayG = np.zeros((512,896,3), np.uint8)
            overlayR = np.zeros((512,896,3), np.uint8)

            overlayB[:,:,0] = np.multiply(blueF[:,:,0] , frame2[0,:,:])
            overlayG[:,:,1] = np.multiply(greenF[:,:,1] , frame2[1,:,:])
            overlayR[:,:,2] = np.multiply(redF[:,:,2], frame2[2,:,:])
            # overlayY[:,:,1] = np.multiply(yellowF[:,:,1] , frame[2,:,:])
            # overlayY[:,:,2] = np.multiply(yellowF[:,:,2] , frame[2,:,:])

            overlay = cv2.resize(frame,(896,512))
            overlay = cv2.addWeighted(overlay, 0.8, overlayB,0.2,0)
            overlay = cv2.addWeighted(overlay, 0.8, overlayG,0.2,0)
            overlay = cv2.addWeighted(overlay, 0.8, overlayR,0.2,0)

            frame2 = (frame2*255).astype(np.uint8)
            frame2 = np.ascontiguousarray(frame2)
            # frame2[:,:,:] = np.where(frame2[:,:,:] > 150, frame2[:,:,:], 0)
            # frame2[1,:,:,:] = np.where(frame2[1,:,:,:] > 250, 255,0)
            # print(fcounter, frame2.shape, frame2)
            

            # cv2.imshow('name1', frame2[0,:,:])
            # cv2.imshow('name2', frame2[1,:,:])
            # cv2.imshow('name3', frame2[2,:,:])
            # cv2.imshow('name4', frame2[3,:,:])

            cv2.imshow('name1', overlay)
            # cv2.imshow('name2', overlayG)
            # cv2.imshow('name3', overlayY)
            # if the frame is available, render detection data on frame and display.
        if frame is not None:
            displayFrame("", frame)

        if cv2.waitKey(1) == ord('q'):
            break
