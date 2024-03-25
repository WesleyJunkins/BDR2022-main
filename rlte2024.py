"""
Mind Monitor - EEG OSC Receiver
Coded: James Clutterbuck (2022)
Requires: pip install python-osc
"""
from datetime import datetime
from multiprocessing.connection import Client
import time
from pythonosc import dispatcher
from pythonosc import osc_server
from codrone_edu.drone import *


c = Client(("localhost", 5001))


ip = "10.122.93.209"
port = 5004
filePath = 'test.csv'
auxCount = -1
recording = False

theta = -1
alpha = -1
beta = -1
engagement = -1
inAir = False
blinkCounter = 0
old_time = -1

f = open (filePath,'w+')

def writeFileHeader():
    global auxCount
    fileString = 'TimeStamp,RAW_TP9,RAW_AF7,RAW_AF8,RAW_TP10,'
    for x in range(0,auxCount):
        fileString += 'AUX'+str(x+1)+','
    fileString +='Marker\n'
    f.write(fileString)

def eeg_handler(address: str,*args):
    global recording
    global auxCount
    global theta
    global beta
    global alpha
    global engagement
    global inAir
    global blinkCounter
    global old_time
    
    if auxCount==-1:
        auxCount = len(args)-4
        writeFileHeader()
    if recording:
        timestampStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        fileString = timestampStr
        if address == "/muse/elements/theta_absolute":
            theta = args[0]
            # print("Theta: ", theta)
        elif address == "/muse/elements/beta_absolute":
            beta = args[0]
            # print("Beta: ", beta)
        elif address == "/muse/elements/alpha_absolute":
            alpha = args[0]
            # print("Alpha: ", alpha)
        elif address == "/muse/elements/jaw_clench":
            print("Jaw Clenched")
            c.send("Jaw Clenched")
            blinkCounter = 0
        elif address == "/muse/elements/blink":
            blinkCounter = blinkCounter + 1
            print("Blinked: ", blinkCounter)
            c.send("Blinked")
    
def marker_handler(address: str,i):
    global recording
    global auxCount
    timestampStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    markerNum = address[-1]
    if recording:
        fileString = timestampStr+',,,,,'
        for x in range (0,auxCount):
            fileString +=','
        fileString +='/Marker/'+markerNum+"\n"
        f.write(fileString)
    if (markerNum=="1"):        
        recording = True
        print("Recording Started.")
    if (markerNum=="2"):
        f.close()
        recording = False
        server.shutdown()
        print("Recording Stopped.")    

if __name__ == "__main__":
    try:
        dispatcher = dispatcher.Dispatcher()
        dispatcher.map("/muse/elements/theta_absolute", eeg_handler)
        dispatcher.map("/muse/elements/alpha_absolute", eeg_handler)
        dispatcher.map("/muse/elements/beta_absolute", eeg_handler)
        dispatcher.map("/muse/elements/jaw_clench", eeg_handler)
        dispatcher.map("/muse/elements/blink", eeg_handler)


        dispatcher.map("/Marker/*", marker_handler)

        server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
        print("Listening on UDP port "+str(port)+"\nSend Marker 1 to Start recording and Marker 2 to Stop Recording.")
        old_time = time.time()
        server.serve_forever()
        
            
    except KeyboardInterrupt:
        drone.close()
    # drone.close()
