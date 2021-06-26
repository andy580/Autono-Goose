import cv2
import depthai as dai
import time
import serial
import cameraSetup
import display
import Car
import Clock

ser = None
# ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
pipeline = cameraSetup.setupPipeline()
car = Car.Car()
timer = Clock.Timekeeper()

with dai.Device() as device:
    device.startPipeline(pipeline)

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

        for t in trackletsData:
            display.annotateFrame(dai, frame, t)
        
        car.getClosestPerson(trackletsData)
        car.controlBrake(timer, ser)
            
        display.showLargeFrame(frame, timer.fps)
        display.consoleOutput(car, timer)
            
        if cv2.waitKey(1) == ord('q'):
            break
