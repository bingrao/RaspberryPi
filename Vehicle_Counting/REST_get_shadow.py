#------------------------------------------
# --- Author: Bing
# --- Version: 1.0
#--- Python Ver: Python 2.7
#--- Description: This code will fetch (GET) the Device Shadw State Doc(Json) from AWS IoT Platform
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
ACCESS_KEY = "AKIAJPY56DIUD7MQIVDQ" # Create one from AWS IAM Module
SECRET_KEY = "xK3Liyj+bIr1ekCjUN/372uCdA1n/lsPt49l4VKe" # Create one from AWS IAM Module
IOT_ENDPOINT = "a2xmpbgswmier.iot.us-west-2.amazonaws.com" # From AWS IoT Dashboard, go to "settings" to find your IoT Endpoint
AWS_REGION = "us-west-2" # Your AWS Region. Full list at - http://docs.aws.amazon.com/general/latest/gr/rande.html#iot_region
HTTPS_ENDPOINT_URL = "https://a2xmpbgswmier.iot.us-west-2.amazonaws.com" # Prefix your AWS IoT Endpoint with "https://"
IoT_THING_NAME = "MyRaspberryPi" # Put your AWS IoT Thing name here.
# ==================================================================
# OPTIONAL VARIABLES  - FEEL FREE TO CHANGE IF YOU KNOW WHAT ARE THESE :-)
HTTPS_METHOD ="GET"
SHADOW_URI = "/things/" + IoT_THING_NAME + "/shadow" # Standard URL
HTTPS_REQUEST_PAYLOAD = ""
# ==================================================================


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
