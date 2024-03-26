from datetime import datetime
from multiprocessing.connection import Client
import time
from pythonosc import dispatcher
from pythonosc import osc_server
from codrone_edu.drone import *

c = Client(("localhost", 5001))

#Setup
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

#Array for Theta, Beta, Alpha waves
brainWaves = [0, 0, 0]

#Engagement for divide-by-zero error
lastEngagement = 0

#Array for holding 5 values
fiveValues = [0, 0, 0, 0, 0]

#Send EEG recordings to server
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
    global brainWaves
    global lastEngagement
    global fiveValues
    
    if auxCount==-1:
        auxCount = len(args)-4
        writeFileHeader()

    #Each time we get 
    if recording:
        timestampStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        fileString = timestampStr

        #Assign Theta, Beta, and Alpha wave values to brainWaves array
        if address == "/muse/elements/theta_absolute":
            theta = args[0]
            brainWaves[0] = theta
        elif address == "/muse/elements/beta_absolute":
            beta = args[0]
            brainWaves[1] = beta
        elif address == "/muse/elements/alpha_absolute":
            alpha = args[0]
            brainWaves[2] = alpha
        if brainWaves[0] != 0 and brainWaves[1] != 0 and brainWaves[2] != 0:

            #Calculate engagement
            if brainWaves[0] + brainWaves[2] != 0:
                engagement = (abs(brainWaves[1]) / (abs(brainWaves[0]) + abs(brainWaves[2])))

                #Calculate the average of 5 values
                fiveValues.pop(0)
                fiveValues.append(engagement)
                average = abs(sum(fiveValues) / 5)

                #Return engagement
                tempString = timestampStr + " " + str(average)
                print(tempString)
                c.send(average)
            else:
                c.send(0)

            #Reset brainWaves
            brainWaves = [0, 0, 0]

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

        dispatcher.map("/Marker/*", marker_handler)

        server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
        print("Listening on UDP port "+str(port)+"\nSend Marker 1 to Start recording and Marker 2 to Stop Recording.")
        old_time = time.time()
        server.serve_forever()
        
    except KeyboardInterrupt:
        pass
    # drone.close()
