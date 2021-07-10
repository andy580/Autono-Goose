import cv2

color = (0, 0, 255)

def annotateFrame(dai, frame, t):
    roi = t.roi.denormalize(frame.shape[1], frame.shape[0])
    x1 = int(roi.topLeft().x)
    y1 = int(roi.topLeft().y)
    x2 = int(roi.bottomRight().x)
    y2 = int(roi.bottomRight().y)

    label = 'person'

    statusMap = {dai.Tracklet.TrackingStatus.NEW : "NEW", dai.Tracklet.TrackingStatus.TRACKED : "TRACKED", dai.Tracklet.TrackingStatus.LOST : "LOST"}
    cv2.putText(frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
    cv2.putText(frame, f"ID: {[t.id]}", (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
    if t.status != t.TrackingStatus.REMOVED:
        cv2.putText(frame, statusMap[t.status], (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

    cv2.putText(frame, f"X: {int(t.spatialCoordinates.x)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
    cv2.putText(frame, f"Y: {int(t.spatialCoordinates.y)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
    cv2.putText(frame, f"Z: {int(t.spatialCoordinates.z)} mm", (x1 + 10, y1 + 95), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)

def showLargeFrame(frame, fps):
    cv2.putText(frame, "NN fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)
    frame = cv2.resize(frame, (1000,1000))
    cv2.imshow("tracker", frame)

def consoleOutput(car, timer):
    if timer.counter == 1:
        print(timer.seconds, car.executingBrake, car.inPath())
        if (timer.seconds==timer.execTime):
            car.executingBrake=False
            print('Done executing')
