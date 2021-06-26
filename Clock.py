import time

class Timekeeper():
    counter = 0
    fps = 0
    seconds = 0
    execTime = 0
    missingPersonTime = 0
    startTime = time.monotonic()

    def updateSeconds(self):
        if self.counter == 0:
            self.seconds +=1

    def updateFPS(self, current_time):
        if (current_time - self.startTime) > 1 :
            self.fps = self.counter / (current_time - self.startTime)
            self.counter = 0
            self.startTime = current_time