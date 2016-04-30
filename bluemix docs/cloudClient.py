#!/usr/bin/env python
import time
import os, json
import ibmiotf.application
import uuid
from time import strftime
#import datetime

roll=""
in_data = 'input.txt'
out_data = 'output.txt'
model = 'model'
options = {
    "org" : "6whyb6",
    "type" : "cloud",
    "id" : "cloud01",
    "auth-method" : "token",
    "auth-key" : "a-6whyb6-nfmbfmzfb2",
    "auth-token" : "v!_FvyTm@HH8!9vSd9",
}


os.chdir("libsvm-3.21")
os.system("make")

fp = open("html.dat", 'a', os.O_NONBLOCK)

   
def myCommandCallback(cmd):
    payload = json.loads(cmd.payload)
    data = payload['data']
    classify(data)

    
def classify(data):
    global in_data, roll
    roll = ""
    for i in data:
        trunc_ = round(float(i), 1)
        if(trunc_<0):
            roll+=str(trunc_)
        else:
            roll+="+"+str(trunc_)
        roll+="#"
    new_line = "0"
    i = 0
    for item in data:
        new_line += " " + str(i) + ":" + str(item)
        i += 1
    f = open(in_data, 'w')
    f.write(new_line)
    f.close()
    output()


def output():
    global in_data, out_data, roll, fp
    model = 'model'
    os.system("./svm-predict" + " " + in_data + " " + model + " " + out_data) 
    f = open (out_data, 'r')
    verdict = f.read()
    f.close()
    if int(verdict[:-1]) < 0:
        dat = {'status':'door closed'}
        roll+="Closed"
        roll+="#"    
    else:
        dat = {'status':'door opened'}
        roll+="Opened"
        roll+="#"
    roll+=strftime("%H:%M:%S")
    roll+="******"
    fp.write(roll)
    fp.flush()
    client.publishEvent("cloud", "cloud01", "doorStatus", "json", dat)
    

try:
    client = ibmiotf.application.Client(options)
    client.connect()
    client.deviceEventCallback = myCommandCallback
    client.subscribeToDeviceEvents(event="doorData")
    while True:
        time.sleep(0.2)
            

except ibmiotf.ConnectionException  as e:
    print e

