#------------------------------------------
# --- Author: Zixia Liu, Bingbing Rao, Lan Luo
# --- Version: 1.0
#--- Python Ver: Python 2.7
#--- Description: This code will Update (POST) the Device Shadw State Doc(Json) on AWS IoT Platform
#---
#--- Refer to following Doc for AWS Device Shadow REST APIs -
#--- http://docs.aws.amazon.com/iot/latest/developerguide/thing-shadow-rest-api.html
#---
#--- Refer to following Document for information about AWS Sig 4 for REST API Calls
#--- http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html#sigv4_signing-steps-summary
#------------------------------------------

import requests, datetime, sys
from aws_sig_ver_4 import get_HTTP_Request_Header


# ==================================================================
# CHANGE VALUES FOR FOLLOWING VARIABLES AS PER YOUR SETUP
ACCESS_KEY = "*" # Create one from AWS IAM Module
SECRET_KEY = "*" # Create one from AWS IAM Module
IOT_ENDPOINT = "*" # From AWS IoT Dashboard, go to "settings" to find your IoT Endpoint
AWS_REGION = "us-west-2" # Your AWS Region. Full list at - http://docs.aws.amazon.com/general/latest/gr/rande.html#iot_region
HTTPS_ENDPOINT_URL = "https://*" # Prefix your AWS IoT Endpoint with "https://"
IoT_THING_NAME = "*" # Put your AWS IoT Thing name here.
# ==================================================================
# OPTIONAL VARIABLES (FEEL FREE TO CHANGE IF YOU KNOW WHAT ARE THESE :-)
HTTPS_METHOD ="POST"
SHADOW_URI = "/things/" + IoT_THING_NAME + "/shadow" # Standard URL
HTTPS_REQUEST_PAYLOAD = ""
# ==================================================================


print "Enter 1 to Turn On the Camera"
print "Enter 2 to Turn OFF the Camera"
print "Enter 3 to exit"
data = raw_input("Select an option:")
if data == "1":
	HTTPS_REQUEST_PAYLOAD = """{"state" : {"reported" : {"Counting" : "ON",""" + """ "Number":""" + str(0) + """, "During":""" + str(0) + """, "Frequency": """+ str(0) + """}}}"""
elif data == "2":
	HTTPS_REQUEST_PAYLOAD = """{"state" : {"reported" : {"Counting" : "OFF",""" + """ "Number":""" + str(0) + """, "During":""" + str(0) + """, "Frequency": """+ str(0) + """}}}"""
elif data == "3":
	sys.exit()
else:
	print("Invalid input try again...")
	sys.exit()


# Construct URL for Post Request
Request_Url = HTTPS_ENDPOINT_URL + SHADOW_URI

# Get HTTP Headers with AWS Signature 4 Signed Authorization Header
Request_Headers = get_HTTP_Request_Header(HTTPS_METHOD, IOT_ENDPOINT, AWS_REGION, SHADOW_URI, ACCESS_KEY, SECRET_KEY, HTTPS_REQUEST_PAYLOAD)

# Make HTTPS Request
HTTP_RESPONSE = requests.request(HTTPS_METHOD, Request_Url, data=HTTPS_REQUEST_PAYLOAD ,headers=Request_Headers)

# Print Response
print "\nHTTP Response Code:" + str(HTTP_RESPONSE.status_code)
print "Response:"
print HTTP_RESPONSE.text
# ==================================================================
