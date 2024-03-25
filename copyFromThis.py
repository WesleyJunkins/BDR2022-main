from multiprocessing.connection import Listener
from threading import Thread
import time

from codrone_edu.drone import *

drone = Drone()
drone.pair()
inAir = False

blinkCounter = 0
# old_time =  time.time()
# client
def child(conn):
    global old_time
    global blinkCounter
    global inAir
    while True:
        msg = conn.recv()
        # this just echos the value back, replace with your custom logic
        print(msg)
        # print("IN CHILD");
        if msg == "Blinked":
            blinkCounter += 1
        if msg == "Jaw Clenched":
            print("Blink Counter ", blinkCounter)
            if blinkCounter == 2:
                if inAir:
                    drone.land()
                    print("Landing")
                else:
                    drone.takeoff()
                    print("Taking off")
                inAir = not inAir
                
            if blinkCounter >= 3:
                print("Moving forward")
                drone.move_forward(60, "cm", 0.5)
            if blinkCounter == 4:
                print("Turning right")
                drone.turn_right()
            if blinkCounter == 5:
                print("Turning left")
                drone.turn_left()
            blinkCounter = 0
        
        # conn.send(msg)

# server
def mother(address):
    serv = Listener(address)
    while True:
        client = serv.accept()
        child(client)
        # print("IN MOTHER")
        if time.time() - old_time > 5:
            print("Blink counter ", blinkCounter)
            blinkCounter = 0
            old_time = time.time()

def timePassed():
    global blinkCounter
    oldtime = time.time()
    inAir = False
    while True:
        if time.time() - oldtime > 5:
            print("Blink Counter ", blinkCounter)
            if blinkCounter == 2:
                if inAir:
                    drone.land()
                    print("Landing")
                else:
                    drone.takeoff()
                    print("Taking off")
                inAir = not inAir
                
            if blinkCounter >= 3:
                print("Moving forward")
                # drone.move_forwar/d(10, "cm", 0.5)
            blinkCounter = 0
            oldtime = time.time()

# thread = Thread(target=timePassed)

# thread.start()
mother(('', 5001))
# print("HELLO")