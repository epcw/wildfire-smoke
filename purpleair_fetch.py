import requests
import json
import pandas as pd
import time
from time import sleep

# NOTE to calculate AQI from sensor data = https://community.purpleair.com/t/how-to-calculate-the-us-epa-pm2-5-aqi/877

with open('api_key.txt') as f:
    api = f.read()

headers= {'X-API-Key': api}

# get list of sensors within lat/long bounding box (defined by NW/SE corners)
# Port Townsend City Hall
NWlat = 48.1162201
NWlng = -122.755863

# Peak of Mt. Rainier
SElat = 46.8555182
SElng = -121.7631845

url = 'https://api.purpleair.com/v1/sensors?fields=pm2.5_24hour,name,latitude,longitude,altitude,date_created,last_seen&max_age=0&modified_since=0&location_type=0&nwlng=' + str(NWlng) + '&nwlat='+ str(NWlat) + '&selng=' + str(SElng) + '&selat=' + str(SElat)

response = requests.get(url, headers=headers)
print(url)
print("Getting list of stations, Status Code: ", response.status_code)

content = json.loads(response.content)
data = content["data"]
columns = content["fields"]

station_list = 'data/pa_station_list.csv'

df = pd.DataFrame(data, columns=columns)
df.to_csv(station_list)

# needed to walk the url request year by year
unix_year = 31556926
# today = int(time.time()) # kinda redundant now that I'm only pulling to end date

# create empty dataframe outside loop to take data
hist_df = pd.DataFrame()

# loop over sensors
for index, row in df.iterrows():
    sensor = row['sensor_index']
    created = row['date_created']
    ended = row['last_seen']

    print('Sensor: ' + str(sensor))
    print('Active from ' +str(created) + 'to ' + str(ended) + '\n    ____________')

    # Start at the created date, then pull one year at a time until you hit today
    for x in range(created, ended, unix_year):
        start_timestamp = x
        if (x + unix_year) < ended:
            end_timestamp = x + unix_year
        else:
            end_timestamp = ended

        # NOW PUT THE URL PULL IN HERE, AND ADD THE SLEEP
        hist_url = 'https://api.purpleair.com/v1/sensors/' + str(sensor) + '/history?start_timestamp=' + str(start_timestamp) + '&end_timestamp=' + str(end_timestamp) + '&average=1440&fields=pm2.5_alt%2C%20pm2.5_alt_a%2C%20pm2.5_alt_b%2C%20pm2.5_atm%2C%20pm2.5_atm_a%2C%20pm2.5_atm_b%2C%20pm2.5_cf_1%2C%20pm2.5_cf_1_a%2C%20pm2.5_cf_1_b'

        # request from API
        hist_response = requests.get(hist_url, headers=headers)

        # read hist_response
        hist_content = json.loads(hist_response.content)

        # pull out data & field names
        hist_data = hist_content["data"]
        hist_columns = hist_content["fields"]

        # dump to dataframe
        temp_df = pd.DataFrame(hist_data, columns=hist_columns)

        # add in station_index
        temp_df.insert(0,'station_index',sensor)

        # append to the bottom of hist_df
        pd.concat([hist_df, temp_df])

        # API guidelines is hit once every 1-10min, so setting at just over a minute
        sleep(62)

# remove all the duplicate column heading rows (this works ASSUMING that all temp_dfs are exactly the same shape and pull the same data in the same order.  Be careful changing the loop above.
hist_df = hist_df.drop_duplicates(keep='first')

# dump to csv
hist_filename = 'data/pa_hist_data.csv'
hist_df.to_csv(hist_filename)
