from multiprocessing.connection import Listener
from threading import Thread
import time
from codrone_edu.drone import *
from codrone_edu.protocol import *

#Setup
drone = Drone()
drone.pair()
inAir = False

#Client
def child(conn):
    global old_time
    global blinkCounter
    global inAir
    while True:
        val = conn.recv()

        #Takeoff and Land
        if val >= 1.5:
            if inAir == False:
                print("Take-Off")
                drone.takeoff()
                inAir = True
        elif val <= 0.25:
            if inAir == True:
                print("Land")
                drone.land()
                inAir = False

#Server
def mother(address):
    serv = Listener(address)
    while True:
        client = serv.accept()
        child(client)

mother(('', 5001))
