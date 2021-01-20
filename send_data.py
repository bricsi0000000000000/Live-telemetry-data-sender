import sys
import json
import requests
import datetime
import base64

#TODO optional port argument

#section_name = sys.argv[1]

#url = "https://localhost:44304/"
url = "https://192.168.1.33:5001/"

response = requests.post(url + "api/Section?date=" + str(datetime.datetime.now()), verify=False)

print(response)
