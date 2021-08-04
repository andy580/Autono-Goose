import cv2
import depthai as dai
import time
import serial
import cameraSetup
import display
import Car
import Clock
import os

timeStamp = time.localtime()
current_time = time.strftime("%H%M%S", timeStamp)

VIDEO_PATH = "/home/andy/Documents/Autono-Goose/videos/"
MONO_LEFT_FILE = 'monoLI-' + current_time + '.h264'
MONO_RIGHT_FILE = 'monoRI-' + current_time + '.h264'
COLOR_MID_FILE = 'colorMI-' + current_time + '.h265'

MONO_LEFT_OUTPUT_FILE = 'monoLO-' + current_time + '.h264'
MONO_RIGHT_OUTPUT_FILE = 'monoRO-' + current_time + '.h264'
COLOR_MID_OUTPUT_FILE = 'colorMO-' + current_time + '.h265'
COLOR_NN_OUTPUT_FILE = 'colorNN-' + current_time +'.avi'
COLOR_DEPTH_OUTPUT_FILE = 'colorDD-' + current_time + '.avi'

out = cv2.VideoWriter(VIDEO_PATH + COLOR_NN_OUTPUT_FILE,cv2.VideoWriter_fourcc('M','J','P','G'), 27, (300,300))
outD = cv2.VideoWriter(VIDEO_PATH + COLOR_DEPTH_OUTPUT_FILE,cv2.VideoWriter_fourcc('M','J','P','G'), 27, (540,360))

try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
except:
    ser = None

pipeline = cameraSetup.setupPipeline()
car = Car.Car()
timer = Clock.Timekeeper()

with dai.Device() as device:
    device.startPipeline(pipeline)

    # Video Recording
    qRgbEnc = device.getOutputQueue('h265', maxSize=30, blocking=False)
    videoFile = open(VIDEO_PATH + COLOR_MID_FILE, 'wb')

    qRightEnc = device.getOutputQueue('right', maxSize=30, blocking=False)
    videoFileRight = open(VIDEO_PATH + MONO_RIGHT_FILE, 'wb')

    qLeftEnc = device.getOutputQueue('left', maxSize=30, blocking=False)
    videoFileLeft = open(VIDEO_PATH + MONO_LEFT_FILE, 'wb')

    depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    

    preview = device.getOutputQueue("preview", 4, False)
    tracklets = device.getOutputQueue("tracklets", 4, False)

    while(True):
        imgFrame = preview.get()
        track = tracklets.get()
        
        timer.updateSeconds()
        timer.counter+=1

        current_time = time.monotonic()
        timer.updateFPS(current_time)

        frame = imgFrame.getCvFrame()
        trackletsData = track.tracklets

        if (timer.seconds < car.setupTime):
            continue

        # Video Recording
        inDepth = depthQueue.get()
        depthFrame = inDepth.getFrame()
        depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
        depthFrameColor = cv2.equalizeHist(depthFrameColor)
        depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_PLASMA)
        depthFrameColor = cv2.resize(depthFrameColor, (540,360))
        cv2.imshow("depth", depthFrameColor)


        while qRgbEnc.has():
            qRgbEnc.get().getData().tofile(videoFile)
        while qRightEnc.has():
            qRightEnc.get().getData().tofile(videoFileRight)
        while qLeftEnc.has():
            qLeftEnc.get().getData().tofile(videoFileLeft)

        for t in trackletsData:
            display.annotateFrame(dai, frame, t)
        
        car.getClosestPerson(trackletsData)
        car.controlBrake(timer, ser)
        car.controlSteering(timer, ser)
            
        display.showLargeFrame(frame, timer.fps)
        out.write(frame)
        outD.write(depthFrameColor)
        display.consoleOutput(car, timer)
            
        if cv2.waitKey(1) == ord('q'):
            break
    
out.release()
print("Converting from h264/265 to mp4")

cmd = "ffmpeg -framerate 25 -i {} {}"

os.system(cmd.format(VIDEO_PATH + MONO_RIGHT_FILE, VIDEO_PATH + MONO_RIGHT_OUTPUT_FILE))
os.system(cmd.format(VIDEO_PATH + MONO_LEFT_FILE, VIDEO_PATH + MONO_LEFT_OUTPUT_FILE))
os.system(cmd.format(VIDEO_PATH + COLOR_MID_FILE, VIDEO_PATH + COLOR_MID_OUTPUT_FILE))


