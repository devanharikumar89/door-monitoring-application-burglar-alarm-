import RPi.GPIO as GPIO
import os, json
import ibmiotf.application
import uuid
import smbus
import time



# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
def read_byte(adr):
	return bus.read_byte_data(address, adr)
 
def read_word(adr):
	high = bus.read_byte_data(address, adr)
	low = bus.read_byte_data(address, adr+1)
	val = (high << 8) + low
	return val
 
def read_word_2c(adr):
	val = read_word(adr)
	if (val >= 0x8000):
		return -((65535 - val) + 1)
	else:
		return val

def sameNature(xlist):
	first = xlist[0]
	if first > 0:
		for elem in xlist:
			if elem < 0:
				return False
	else:
		for elem in xlist:
			if elem > 0:
				return False
	return True
	
def process_(allattributes):
	max_attributes = 4
	attribs = []
	length = len(allattributes)
	quotient = length/max_attributes
	remainder = length%max_attributes
	i=0
	j=0
	sum_=0
	while i<length:
		sum_+=allattributes[i]
		i+=1
		
		if i%quotient == 0:
			j+=1
			if j==max_attributes:
				while i<length:
					sum_+=allattributes[i]
					i+=1
				avg = float(sum_)/(quotient+remainder)
				attribs.append(avg)
				break
			avg = float(sum_)/quotient
			attribs.append(avg)
			sum_=0
	return attribs
	
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command
 
# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

gyro_xdata = []
stationary = True
nextStatus = None
threshold = 10
cntr = 0

options = {
	"org" : "6whyb6",
	"type" : "raspberrypi",
	"id" : "b827eb32ac06",
	"auth-method" : "token",
	"auth-key" : "a-6whyb6-nfmbfmzfb2",
	"auth-token" : "v!_FvyTm@HH8!9vSd9",
}

def myCommandCallback(cmd):
	if cmd.event == "light":
		payload = json.loads(cmd.payload)
		command = payload["command"]
		#print command
		if command == "on":
			GPIO.output(18, True)
		elif command == "off":
			GPIO.output(18, False)

client = None
try:
	#options = ibmiotf.application.ParseConfigFile("/home/pi/device.cfg")


	client = ibmiotf.application.Client(options)
	client.connect()
	client.deviceEventCallback = myCommandCallback


	while True:
		gyro_xout = read_word_2c(0x43)
		scaled_x = gyro_xout/131
		
		if(abs(scaled_x)>threshold and stationary):
			stationary=False
			if(scaled_x>threshold):
				nextStatus='open'
			if(scaled_x<(-1*threshold)):
				nextStatus='close'
		
		if(not stationary and abs(scaled_x)>threshold):
			gyro_xdata.append(scaled_x)
		
		if(not stationary and abs(scaled_x)<threshold):
			stationary=True
			cntr+=1
			#print "Before model", " : ", nextStatus
			if len(gyro_xdata) > 3 and sameNature(gyro_xdata):
				attribs = process_(gyro_xdata)
				print attribs
				myData = {'data' : attribs}
				client.publishEvent("raspberrypi", "b827eb32ac06", "doorData", "json", myData)
				#print "JSON Published"

			gyro_xdata[:]=[]
			

		time.sleep(0.1)


except ibmiotf.ConnectionException  as e:
	print e



