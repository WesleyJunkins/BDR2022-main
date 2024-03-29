from multiprocessing.connection import Listener
from threading import Thread
import time
from codrone_edu.drone import *
from codrone_edu.protocol import *
from numpy import clip
import keyboard

# Setup
drone = Drone()
drone.pair()
inAir = False
landingVal = 0.5
takeoffVal = 2
scalingVal = 50
normFactor = 5.0

# Client
def child(conn):
    global old_time
    global blinkCounter
    global inAir
    global landingVal
    global takeoffVal
    global scalingVal

    while True:
        val = conn.recv()

        # Takeoff and Land
        # Drone up
        if inAir == True:
            # Moving the drone
            if val >= landingVal:
                # Add more functions here
                if val >= 0.75:
                    # Move forward
                    print("Moving Forward")
                    pitch = clip((val/upperThresh) * scalingVal, 0, scalingVal)
                    pitch = int(pitch)
                    print(pitch)
                    drone.go(0, pitch, 0, 0, 0.5)
            # Land
            elif val < landingVal:
                if inAir == True:
                    print("Landing")
                    drone.land()
                    inAir = False
        # Drone down
        elif inAir == False:
            # Takeoff
            if val >= takeoffVal:
                print("Taking Off")
                drone.takeoff()
                inAir = True

# Server
def mother(address):
    serv = Listener(address)
    while True:
        client = serv.accept()
        child(client)

try:
    mother(("", 5001))
# Emergency landing
except KeyboardInterrupt:
    drone.land()
    drone.close()