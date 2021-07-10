import depthai as dai
import argparse

# Start defining a pipeline

labelMap = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

nnPath = 'models/mobilenet-ssd_openvino_2021.2_6shave.blob'

def setupPipeline():
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

    monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
    monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
    monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
    monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

    # setting node configs
    median = dai.StereoDepthProperties.MedianFilter.KERNEL_7x7
    stereo.setConfidenceThreshold(255)
    stereo.setMedianFilter(median)

    spatialDetectionNetwork.setBlobPath(nnPath)
    spatialDetectionNetwork.setConfidenceThreshold(0.2)
    spatialDetectionNetwork.input.setBlocking(False)
    spatialDetectionNetwork.setBoundingBoxScaleFactor(0.1)
    spatialDetectionNetwork.setDepthLowerThreshold(200)
    spatialDetectionNetwork.setDepthUpperThreshold(15000)

    # Create outputs
    monoLeft.out.link(stereo.left)
    monoRight.out.link(stereo.right)

    # Link plugins CAM . NN . XLINK
    colorCam.preview.link(spatialDetectionNetwork.input)
    objectTracker.passthroughTrackerFrame.link(xoutRgb.input)

    objectTracker.setDetectionLabelsToTrack([15])  # track only person

    # take the smallest ID when new object is tracked, possible options: SMALLEST_ID, UNIQUE_ID
    objectTracker.setTrackerIdAssigmentPolicy(dai.TrackerIdAssigmentPolicy.SMALLEST_ID)
    objectTracker.out.link(trackerOut.input)

    spatialDetectionNetwork.passthrough.link(objectTracker.inputTrackerFrame)
    spatialDetectionNetwork.passthrough.link(objectTracker.inputDetectionFrame)
    spatialDetectionNetwork.out.link(objectTracker.inputDetections)

    stereo.depth.link(spatialDetectionNetwork.inputDepth)

    return pipeline




    