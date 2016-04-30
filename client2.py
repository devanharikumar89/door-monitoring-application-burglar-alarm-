import time
import os, json
import ibmiotf.application
import uuid
from time import strftime

client = None

options = {
	"org" : "6whyb6",
	"type" : "laptop",
	"id" : "device01",
	"auth-method" : "token",
	"auth-key" : "a-6whyb6-nfmbfmzfb2",
	"auth-token" : "v!_FvyTm@HH8!9vSd9", 
}
   
def myCommandCallback(cmd):
	payload = json.loads(cmd.payload)
	data = payload["status"]
	print data+" "+strftime("%H:%M:%S",time.gmtime())



try:
	client = ibmiotf.application.Client(options)
	client.connect()
	client.deviceEventCallback = myCommandCallback
	client.subscribeToDeviceEvents(event="doorStatus")

	while True:
		time.sleep(0.2)
			

except ibmiotf.ConnectionException  as e:
	print e


