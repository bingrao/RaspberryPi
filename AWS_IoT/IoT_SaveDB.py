#------------------------------------------
# --- Author: Bing
# --- Version: 1.0
# --- Description: This python script will leverage AWS IoT Shadow to control Camera
# ------------------------------------------

# Import package
import sys
import ssl
import json
import paho.mqtt.client as mqtt

# for motion sensor
import RPi.GPIO as GPIO
import time
from datetime import datetime


# =======================================================
# Set Following Variables
# AWS IoT Endpoint
MQTT_HOST = "a2xmpbgswmier.iot.us-west-2.amazonaws.com"
# CA Root Certificate File Path
CA_ROOT_CERT_FILE = "/home/pi/Documents/Amazon/rootCA.pem.crt"
# AWS IoT Thing Name
THING_NAME = "MyRaspberryPi"
# AWS IoT Thing Certificate File Path
THING_CERT_FILE = "/home/pi/Documents/Amazon/91eb2ca420-certificate.pem.crt"
# AWS IoT Thing Private Key File Path
THING_PRIVATE_KEY_FILE = "/home/pi/Documents/Amazon/91eb2ca420-private.pem.key"
# =======================================================


# =======================================================
# No need to change following variables
MQTT_PORT = 8883
MQTT_KEEPALIVE_INTERVAL = 45
SHADOW_UPDATE_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update"
SHADOW_UPDATE_ACCEPTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/accepted"
SHADOW_UPDATE_REJECTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/rejected"
SHADOW_UPDATE_DELTA_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/delta"
SHADOW_GET_TOPIC = "$aws/things/" + THING_NAME + "/shadow/get"
SHADOW_GET_ACCEPTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/get/accepted"
SHADOW_GET_REJECTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/get/rejected"
SHADOW_STATE_DOC_Camera_ON = """{"state" : {"reported" : {"Camera" : "ON"}}}"""
SHADOW_STATE_DOC_Camera_OFF = """{"state" : {"reported" : {"Camera" : "OFF"}}}"""
# =======================================================


#creating a client with client-id=mqtt-test
mqttc = mqtt.Client(client_id="Bing")



#called while client tries to establish connection with the server
def on_connect(mqttc, obj, flags, rc):
    if rc==0:
        print ("Subscriber Connection status code: "+str(rc)+" | Connection status: successful")
        mqttc.subscribe("SHADOW_UPDATE_ACCEPTED_TOPIC", qos=0)
    elif rc==1:
        print ("Subscriber Connection status code: "+str(rc)+" | Connection status: Connection refused")

#called when a topic is successfully subscribed to
def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos)+"data"+str(obj))

#called when a message is received by a topic
def on_message(mqttc, obj, msg):
    print("Received message from topic: "+msg.topic+" | QoS: "+str(msg.qos)+" | Data Received: "+str(msg.payload))


mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message


# Configure TLS Set
mqttc.tls_set(CA_ROOT_CERT_FILE, certfile=THING_CERT_FILE, keyfile=THING_PRIVATE_KEY_FILE, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

# Connect with MQTT Broker
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
#automatically handles reconnecting
#start a new thread handling communication with AWS IoT
mqttc.loop_start()

sensor = 12

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor,GPIO.IN)

rc=0
try:
    while rc == 0:
        i = GPIO.input(sensor)
        print(i)     # i = 1: Motion detected; i = 0: No Motion
        data={}
        data['motion']=i
        data['time']=datetime.now().strftime('%Y/%m/%d %H:%M:%s')
        playload = '{"state":{"reported":'+json.dumps(data)+'}}'
        print(playload)

        #the topic to publish to
        #the names of these topics start with $aws/things/thingName/shadow.
        msg_info = mqttc.publish(SHADOW_UPDATE_TOPIC, playload, qos=1)

        time.sleep(5)

except KeyboardInterrupt:
    pass

GPIO.cleanup()
