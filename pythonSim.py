import time
import serial
from random import randint
from random import seed

seed(1)

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

while(True):
    randNum = randint(0,1)

    if (randNum == 0):
        ser.write(b'g')
    elif (randNum == 1):
        ser.write(b's')
    print(randNum, flush=True)

    time.sleep(1)