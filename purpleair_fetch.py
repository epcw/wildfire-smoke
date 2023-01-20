import requests
import json
import pandas as pd

# NOTE to calculate AQI from sensor data = https://community.purpleair.com/t/how-to-calculate-the-us-epa-pm2-5-aqi/877

with open('api_key.txt') as f:
    api = f.read()

headers= {'X-API-Key': api}

# get list of sensors within lat/long bounding box (defined by NW/SE corners)
# Port Townsend City Hall
NWlng = 48.1162201
NWlat = -122.755863

# Peak of Mt. Rainier
SElng = 46.8555182
SElat = -121.7631845

url = 'https://api.purpleair.com/v1/sensors?fields=pm2.5&location_type=0&nwlng=' + str(NWlng) + '&nwlat='+ str(NWlat) + '&selng=' + str(SElng) + '&selat=' + str(SElat)
# url = 'https://api.purpleair.com/v1/sensors?fields=pm2.5_24hour,name,latitude,longitude,altitude,date_created,&location_type=0&nwlng=' + str(NWlng) + '&nwlat='+ str(NWlat) + '&selng=' + str(SElng) + '&selat=' + str(SElat)

response = requests.get(url, headers=headers)
print(url)
print("Status Code: ", response.status_code)

content = json.loads(response.content)
data = content["data"]
columns = content["fields"]

df = pd.DataFrame(data, columns=columns)
print(df.shape)
