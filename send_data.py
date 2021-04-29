import requests
from datetime import datetime
import time
import json
import warnings
from requests.exceptions import ConnectionError

# ---------------------CONFIGURATION--------------------------------------------------------------------------------------------
configuration = json.loads(open("configuration_files/configuration.json", "r").read())

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
# ------------------------------------------------------------------------------------------------------------------------------

can_send_data = False

live_section_id = -1

stop_sending_data = False

# ---------------------SENSOR DATA----------------------------------------------------------------------------------------------
times = []
times_index = 0
times_buffer = []

speeds = []
speeds_index = 0
speeds_buffer = []

buffer_size = 0

package_ID = 0;
# ------------------------------------------------------------------------------------------------------------------------------

# ---------------------TEMPORARY DATA COLLECTION SIMULATION---------------------------------------------------------------------
file = open("data_files/time", "r")
input = file.read()
for data in input.split(';'):
  times.append(float(data.replace(' ','').replace(',','.')))

file = open("data_files/speed", "r")
input = file.read()
for data in input.split(';'):
  speeds.append(float(data.replace(' ','').replace(',','.')))

#print(len(speeds))
# ------------------------------------------------------------------------------------------------------------------------------
'''
import matplotlib.pyplot as plt
plt.plot(speeds)
plt.savefig('speeds.png')
'''
# ---------------------CREATE PACKAGE-------------------------------------------------------------------------------------------
def MakePackage():
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
  """.format(live_section_id, str(datetime.now().timestamp()), str(speeds_buffer)[1:len(str(speeds_buffer))-1], str(times_buffer)[1:len(str(times_buffer)) - 1])
  package = package.replace("'","\"")
  #print(package)
  return package
# ------------------------------------------------------------------------------------------------------------------------------

while stop_sending_data == False:
# ----------ALWAYS CHECK IF THE LIVE STATUS OF THE LIVE SECTION IS CHANGED------------------------------------------------------
  try:
    section_get_request = requests.get(URL + GET_LIVE_SECTION_API_CALL, verify = False)
    if section_get_request.status_code == HTTP_STATUS_CODE_OK:
      try:
        live_section_id = section_get_request.json()["id"]
        can_send_data = True
      except Exception as e:
        print("There was a problem getting the ID of the live section. Trying again in " + str(WAIT_BETWEEN_TRIES) + " seconds. Error: " + str(e.__class__))
        time.sleep(WAIT_BETWEEN_TRIES)
    else:
      print("There is no live section at the moment. Trying again in " + str(WAIT_BETWEEN_TRIES) + " seconds")
      time.sleep(WAIT_BETWEEN_TRIES)
  except Exception as e:
    print("There is no connection to the server. Trying again in " + str(WAIT_BETWEEN_TRIES) + " seconds")
    time.sleep(WAIT_BETWEEN_TRIES)
# ------------------------------------------------------------------------------------------------------------------------------

# ---------------------IF THERE IS A LIVE SECTION, COLLECT DATA-----------------------------------------------------------------
  if can_send_data == True:
    if times_index >=len(times):
      stop_sending_data = True
    else:
      if len(times_buffer) == MAX_BUFFER_SIZE:
        package = MakePackage()
        successfull = False
        while successfull == False:
          try:
            send_package_response = requests.post(URL + POST_PACKAGE_API_CALL + package, verify = False)
            successfull = send_package_response.status_code == HTTP_STATUS_CODE_OK
          except Exception as e:
            print("There is no connection to the server. Trying again in " + str(WAIT_BETWEEN_TRIES) + " seconds")
            time.sleep(WAIT_BETWEEN_TRIES)
            
          if successfull == False:
            print("An error occurred while sending package [" + str(package_ID) + "]. HTTP status code: " + str(send_package_response.status_code))

        if successfull == True:    
          print("Package [" + str(package_ID) + "] sent successfully to section [" + str(live_section_id) + "]")

        time.sleep(WAIT_BETWEEN_SENDING)
        times_buffer = []
        speeds_buffer = []
        package_ID = package_ID + 1
      else:
        # COLLECTING DATA | TODO: later replace with CAN communication
        if times_index < len(times):
          times_buffer.append({"value" : times[times_index]})
          times_index = times_index + 1
        
        if speeds_index < len(speeds):
          speeds_buffer.append({"value" : speeds[speeds_index]})
          speeds_index = speeds_index + 1
# ------------------------------------------------------------------------------------------------------------------------------

print("------------------------")
print("Stopped sending data")
print("Summary:")
print("\tAll sent packages: " + str(package_ID))
print("------------------------")
