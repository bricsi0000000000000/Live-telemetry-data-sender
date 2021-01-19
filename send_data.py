from random import *
import time
import datetime

values = []

for number in range(100):
  values.append(randrange(100)/100)
  #values.append(number)

channelsUrl = "https://localhost:44332/api/Channels"
inputFileUrl = "https://localhost:44332/api/File"

currentDate = datetime.datetime.now()
date = currentDate.strftime("%Y.%m.%d")
fileName = "proba_file.json"

import json
import requests

file = {
  "name": fileName,
  "date": date,
  "end": "true"
}

r = requests.post(inputFileUrl, json=file, verify=False)

index = 0
while index < len(values):
  buffer = []
  for i in range(5):
    buffer.append(values[index])
    index = index + 1

  channel = {
    "inputFileName": fileName,
    "name": "proba",
    "values": buffer
  }

  r = requests.post(channelsUrl, json=channel, verify=False)

  time.sleep(0.1)


file = {
  "name": fileName,
  "date": date,
  "end": "true"
}

r = requests.post(inputFileUrl, json=file, verify=False)

print("end")