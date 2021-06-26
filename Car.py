import numpy as np

class Car():
    executingBrake = False
    executingSteering = False
    brake = True
    lostPerson = False
    visiblePerson = False
    steeringPosition = 'n' #can be 'l', 'n', 'r'
    stoppingDistance = 1200
    executionSeconds = 3
    missingPersonSeconds = 2
    setupTime = 1

    closestPerson = None

    def controlBrake(self, timer, ser):
        if (self.visiblePerson == False):
            self.updateLostPersonTracker(timer)
        elif(self.closestPerson.spatialCoordinates.z <= self.stoppingDistance):           
            self.executeBrake(timer, ser)
        else:
            self.releaseBrake(timer, ser)
        self.checkLostPerson(timer, ser)
        self.updateVisiblePerson(timer)

    def controlSteering():
        pass 
        # TODO

    def updateVisiblePerson(self, timer):
        if self.closestPerson != None and self.closestPerson.status == self.closestPerson.TrackingStatus.TRACKED:
            self.visiblePerson = True
        else:
            if (timer.missingPersonTime == timer.seconds):
                self.lostPerson=True
            elif timer.missingPersonTime < timer.seconds:
                timer.missingPersonTime = timer.seconds + self.missingPersonSeconds

    def getClosestPerson(self, trackletsData):
        if (len(trackletsData)>0):
            self.closestPerson = trackletsData[0]
            for t in trackletsData:
                if(t.spatialCoordinates.z < self.closestPerson.spatialCoordinates.z):
                    self.closestPerson = t
        else:
            self.closestPerson = None
            self.visiblePerson = False

    def updateLostPersonTracker(self,timer):
        if (timer.missingPersonTime == timer.seconds):
            self.lostPerson=True
        elif timer.missingPersonTime < timer.seconds:
            timer.missingPersonTime = timer.seconds + self.missingPersonSeconds

    def checkLostPerson(self, timer, ser):
        if (self.executingBrake==False and self.brake==False and self.lostPerson==True):
            print('lost person')
            print(b's', flush=True)   
            if ser!= None:
                ser.write(b's')  
            self.executingBrake=True
            timer.execTime = timer.seconds+self.executionSeconds
            self.brake = True   

    def executeBrake(self, timer, ser):
        if (self.executingBrake==False and self.brake==False):
            print(b's', flush=True)
            if ser!=None:
                ser.write(b's')
            self.executingBrake=True
            timer.execTime = timer.seconds+self.executionSeconds
            self.brake = True
            self.lostPerson = False

    def releaseBrake(self,timer, ser):
        if (self.executingBrake==False and self.brake==True and self.visiblePerson == True) :
                print(self.closestPerson.spatialCoordinates.z)
                print(b'g', flush=True)
                if ser!=None:
                    ser.write(b'g')
                self.executingBrake=True
                timer.execTime = timer.seconds+self.executionSeconds
                self.brake = False
                self.lostPerson = False

    def inPath(self):
        inPath = bool( (900-(np.tan(np.deg2rad(5))*t.spatialCoordinates.z)) >0 )   
        return inPath

         
        


