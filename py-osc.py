"""
Mind Monitor - EEG OSC Receiver
Coded: James Clutterbuck (2022)
Requires: pip install python-osc
"""
from datetime import datetime
from pythonosc import dispatcher
from pythonosc import osc_server

ip = "10.122.126.40"
port = 5003
filePath = 'OSC-Python-Recording.csv'
auxCount = -1
recording = False

f = open (filePath,'w+')

def writeFileHeader():
    global auxCount
    fileString = 'TimeStamp,Delta_TP9,Delta_AF7,Delta_AF8,Delta_TP10,Theta_TP9,Theta_AF7,Theta_AF8,Theta_TP10,Alpha_TP9,Alpha_AF7,Alpha_AF8,Alpha_TP10,Beta_TP9,Beta_AF7,Beta_AF8,Beta_TP10,Gamma_TP9,Gamma_AF7,Gamma_AF8,Gamma_TP10'
    for x in range(0,auxCount):
        fileString += 'AUX'+1str(x+1)+','
    fileString +='Marker\n'
    f.write(fileString)

def eeg_handler(address: str,*args):
    print("ARGS: ", args)
    global recording
    global auxCount
    if auxCount==-1:
        auxCount = len(args)-4
        writeFileHeader()
    if recording:
        timestampStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        fileString = timestampStr
        for arg in args:
            fileString += ","+str(arg)            
        fileString+="\n"
        f.write(fileString)
    
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
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/muse/eeg", eeg_handler)
    dispatcher.map("/Marker/*", marker_handler)

    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
    print("Listening on UDP port "+str(port)+"\nSend Marker 1 to Start recording and Marker 2 to Stop Recording.")
    server.serve_forever()