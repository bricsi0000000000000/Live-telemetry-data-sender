import requests
import datetime
import time
import json

#TODO config file: IP address, port, sleep_time.

HTTP_STATUS_CODE_OK = 200
WAIT_BETWEEN_TRIES = 3 # in seconds
WAIT_BETWEEN_SENDING = 1 # in seconds
MAX_BUFFER_SIZE = 5
URL = "http://192.168.1.33:5000/"

can_send_data = False

live_section_id = -1

yaw_angle = []
yaw_angle_index = 0

buffer_size = 0
buffer = []

file = open("yaw_angle", "r")
input = file.read()
for data in input.split(';'):
  yaw_angle.append(float(data.replace(',','.')))

while True:
  if(can_send_data == False):
    try:
      section_get_request = requests.get(URL + "api/Section/live", verify = False)
      if section_get_request.status_code == HTTP_STATUS_CODE_OK:
        can_send_data = True
        live_section_id = section_get_request.json()["id"]
      else:
        time.sleep(WAIT_BETWEEN_TRIES)
    except:
      print("Can't connect to the sever")
  else:
    if len(buffer) == MAX_BUFFER_SIZE:
      successfull = False
      while successfull == False:
        try:
          print(str(buffer))
          send_yaw_angle_response = requests.post(URL + "api/YawAngle?values=" + str(buffer) + "&sectionID=" + str(live_section_id), verify = False)
          successfull = send_yaw_angle_response.status_code == HTTP_STATUS_CODE_OK
        except:
          print("Can't connect to the sever")
          
        if successfull == False:
          print("An error occurred while sending data")
          
      print("Data sent successfully")

      time.sleep(WAIT_BETWEEN_SENDING)
      buffer = []
    else:
      if yaw_angle_index < len(yaw_angle):
        buffer.append({"value" : yaw_angle[yaw_angle_index]})
        yaw_angle_index = yaw_angle_index + 1
