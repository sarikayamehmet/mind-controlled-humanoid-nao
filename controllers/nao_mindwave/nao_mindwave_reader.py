# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 15:20:12 2020

@author: MAS
"""

import socket
import json
import time

#Experiment duration
duration = 900 # seconds

outfile="data_eeg.csv";
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 13854) #Default mindwave port
sock.connect(server_address)
command = "{\"enableRawOutput\": false, \"format\": \"Json\"}\n"

def writeFile(outputstr):
    outfptr = open(outfile,'a');
    outfptr.write(outputstr+"\n");
    outfptr.close()

def collect_data():
    sent = sock.send(command.encode('ascii'))
    data = sock.recv(2048)
    poorSignalLevel=blinkStrength=attention=meditation=0
    #Example data:
    #{"eSense":{"attention":91,"meditation":41},"eegPower":{"delta":1105014,"theta":211310,"lowAlpha":7730,"highAlpha":68568,"lowBeta":12949,"highBeta":47455,"lowGamma":55770,"highGamma":28247},"poorSignalLevel":0}
    start_time = time.perf_counter()
    while time.perf_counter() - start_time < duration:
        data = sock.recv(2048).decode('utf-8')
        try:
            eeg = json.loads(data)
        except:
            print("Invalid json format!!!")
            continue
        poorSignalLevel=blinkStrength=attention=meditation=0
        if 'blinkStrength' in eeg:
            blinkStrength = eeg['blinkStrength']
    
        if 'poorSignalLevel' in eeg:
            poorSignalLevel = eeg['poorSignalLevel']
            
        if 'eSense' in eeg:
            attention = eeg['eSense']['attention']
            meditation = eeg['eSense']['meditation']
        
        outputstr = str(poorSignalLevel)+","+str(blinkStrength)+","+str(attention)+","+str(meditation)
        writeFile(outputstr)
        time.sleep(0.3)
    sock.close()

if __name__ == "__main__":
    collect_data()