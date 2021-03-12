import time
from random import randint
from random import seed

seed(1)

while(True):
    direction = randint(0,2)
    print(direction, flush=True)
    time.sleep(1)