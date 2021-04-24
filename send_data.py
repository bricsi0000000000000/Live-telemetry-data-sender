import requests
from datetime import datetime
import time
import json
import warnings

# ---------------------CONFIGURATION-------------------------------------------
configuration = json.loads(open("configuration.json", "r").read())

if configuration['ignore_warnings'] == True:
  warnings.filterwarnings("ignore")

HTTP_STATUS_CODE_OK = int(configuration['HTTP_status_code_ok'])
WAIT_BETWEEN_TRIES = int(configuration['wait_between_tries']) # in seconds
WAIT_BETWEEN_SENDING = int(configuration['wait_between_sending']) # in seconds
MAX_BUFFER_SIZE = int(configuration['max_buffer_size'])
GET_LIVE_SECTION_API_CALL = configuration['get_live_section_api_call']
POST_PACKAGE_API_CALL = configuration['post_package_api_call']
URL = "{0}://{1}:{2}/".format('https' if configuration['isHTTPS'] == True else 'http',
                              configuration['url'],
                              configuration['port'])
# -----------------------------------------------------------------------------

can_send_data = False

live_section_id = -1

# ---------------------SENSOR DATA---------------------------------------------
times = []
times_index = 0
times_buffer = []

speeds = []
speeds_index = 0
speeds_buffer = []

buffer_size = 0

package_ID = 0;
package = ""
# -----------------------------------------------------------------------------

# ---------------------TEMPORARY DATA COLLECTION SIMULATION--------------------
file = open("time", "r")
input = file.read()
for data in input.split(';'):
  times.append(float(data.replace(' ','').replace(',','.')))

file = open("speed_from_db", "r")
input = file.read()
for data in input.split(';'):
  speeds.append(float(data.replace(' ','').replace(',','.')))
# -----------------------------------------------------------------------------
'''
import matplotlib.pyplot as plt
plt.plot(speeds)
plt.savefig('speeds.png')
'''
# ---------------------CREATE PACKAGE------------------------------------------
def MakePackage():
  global package
  converted_speeds = []
  for current_speed in speeds_buffer:
    converted_speeds.append(current_speed)

  converted_times = []
  for current_time in times_buffer:
    converted_times.append(current_time)

  package = """
  {{
    "sectionID": {0},
    "sentTime": {1},
    "speeds": [
      {2}
    ],
    "times": [
      {3}
    ]
  }}
  """.format(live_section_id, str(datetime.now().timestamp()), str(converted_speeds)[1:len(str(converted_speeds))-1], str(converted_times)[1:len(str(converted_times)) - 1])
  package = package.replace("'","\"")
  #print(package)
# -----------------------------------------------------------------------------

# ---------------------COLLECTING AND SENDING DATA-----------------------------
while True:
  try:
    section_get_request = requests.get(URL + GET_LIVE_SECTION_API_CALL, verify = False)
    if section_get_request.status_code == HTTP_STATUS_CODE_OK:
      can_send_data = True
      try:
        live_section_id = section_get_request.json()["id"]
      except Exception as e:
        print("Trying again in " + str(WAIT_BETWEEN_TRIES) + " seconds.. " + str(e.__class__))
        time.sleep(WAIT_BETWEEN_TRIES)
    else:
      print("Trying again in " + str(WAIT_BETWEEN_TRIES) + " seconds..")
      time.sleep(WAIT_BETWEEN_TRIES)
  except Exception as e:
    print("Trying.. " + str(e.__class__))
    time.sleep(WAIT_BETWEEN_TRIES)
    
  if(can_send_data == True):
    if len(times_buffer) == MAX_BUFFER_SIZE:
      MakePackage()
      successfull = False
      while successfull == False:
        try:
          send_package_response = requests.post(URL + POST_PACKAGE_API_CALL + package, verify = False)
          successfull = send_package_response.status_code == HTTP_STATUS_CODE_OK
        except Exception as e:
          print("Can't send data.. " + str(e.__class__))
          time.sleep(WAIT_BETWEEN_TRIES)
          
        if successfull == False:
          print("An error occurred while sending package")

      if successfull == True:    
        print("Package sent successfully")

      time.sleep(WAIT_BETWEEN_SENDING)
      times_buffer = []
      speed_buffer = []
    else:
      # COLLECTING DATA | TODO: later replace with CAN communication
      if times_index < len(times):
        times_buffer.append({"id" : times_index, "value" : times[times_index]})
        times_index = times_index + 1
      
      if speeds_index < len(speeds):
        speeds_buffer.append({"id" : speeds_index, "value" : speeds[speeds_index]})
        speeds_index = speeds_index + 1
# -----------------------------------------------------------------------------
