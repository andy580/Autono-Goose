import time
import serial
from random import randint
from random import seed

seed(1)

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

while(True):
    randNum = randint(0,1)

    if randNum == 0:
        direction = 'l'
    elif randNum == 1:
        direction = 'r'
    print(direction, flush=True)

    # If we want python to directly communicate with arduino
    # print(direction)
    # if (direction == 0):
    #     ser.write(b"l")
    # elif (direction == 1):
    #     ser.write(b"r")
    time.sleep(1)