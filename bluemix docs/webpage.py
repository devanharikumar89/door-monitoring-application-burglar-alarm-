from flask import Flask,redirect
from flask import render_template
from flask import request
import os, json
import time
import ibmiotf.application
import threading

client = None
deviceId = os.getenv("DEVICE_ID")
vcap = json.loads(os.getenv("VCAP_SERVICES"))
app = Flask(__name__)
port = os.getenv('VCAP_APP_PORT', '5000')
os.system('./cloudClient.py &')

os.chdir("libsvm-3.21")
fp = open("html.dat", 'r', os.O_NONBLOCK)


@app.route('/')
def hello():
    return '<!doctype html>\n<html><head><title>Door Monitor</title></head><body><h1>Data received on Bluemix</h1> <br /><form action="/refreshcalled" method="GET"> <input type="submit" value="Refresh"> </form><br /></body></html>'

@app.route('/refresh')
def ref():
    global update, fp
    htmlstart = '<!doctype html>\n<html><head><title>Door Monitor</title></head><body><h1>Data received on Bluemix</h1> <br /><form action="/refreshcalled" method="GET"> <input type="submit" value="Refresh"> </form><br />Value 1 &nbsp&nbsp&nbsp&nbsp&nbsp Value 2 &nbsp&nbsp&nbsp&nbsp&nbsp Value 3 &nbsp&nbsp&nbsp&nbsp&nbsp Value 4 &nbsp&nbsp&nbsp&nbsp Verdict &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp Timestamp<br /><br />'
    htmlend = '</body></html>'
    fp.seek(0)
    dat=fp.read()
    inner=""
    subentrylist=[]
    if dat:
        entry_ = dat.split("******")
        subentrylist[:]=[]
        final_ =""
        for subentry in entry_:
            subentrylist=subentry.split("#")
            final_ = "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp".join(subentrylist)
            final_ += "<br />"
            inner+=final_
    else:
        inner='No data'
    dat=''
    return htmlstart+inner+htmlend



@app.route('/refreshcalled', methods=['GET'])
def light_route():
    return redirect("/refresh", code=302)

options = {
        "org": vcap["iotf-service"][0]["credentials"]["org"],
        "id": vcap["iotf-service"][0]["credentials"]["iotCredentialsIdentifier"],
        "auth-method": "apikey",
        "auth-key": vcap["iotf-service"][0]["credentials"]["apiKey"],
        "auth-token": vcap["iotf-service"][0]["credentials"]["apiToken"]
    }
client = ibmiotf.application.Client(options)

if __name__ == "__main__":    
    print('in main')
    port = int(port)
    app.run(host='0.0.0.0', port=int(port))
    
