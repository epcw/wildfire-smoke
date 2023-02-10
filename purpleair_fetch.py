import requests
import json
import pandas as pd
from datetime import datetime
from time import sleep
from fastparquet import ParquetFile as pf
from fastparquet import write as pw

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

# create empty dataframe outside loop to take data
# hist_df = pd.DataFrame(columns=['','station_index','time_stamp','pm2.5_alt','pm2.5_alt_a','pm2.5_alt_b','pm2.5_atm','pm2.5_atm_a','pm2.5_atm_b','pm2.5_cf_1','pm2.5_cf_1_a','pm2.5_cf_1_b'])
hist_df = pd.DataFrame(columns=['','station_index','time_stamp','pm2.5_alt','pm2.5_atm','pm2.5_AVG'])
hist_filename = 'data/pa_hist_data.parquet'

# STATION LIST LOOP - COMMENT OUT IF RESTARTING
response = requests.get(url, headers=headers)
print(url)
print("Getting list of stations, Status Code: ", response.status_code)

content = json.loads(response.content)
data = content["data"]
columns = content["fields"]

station_list = 'data/pa_station_list.parquet'

df = pd.DataFrame(data, columns=columns)
pw(station_list, df)

# COMMENT OUT IF ADDING TO EXISTING
pw(hist_filename, hist_df, compression='GZIP')

# LOAD STATION LIST (if not fetching, as when restarting script)
# station_filename = 'data/pa_station_list.parquet'
# parqf = pf(station_filename)
# df = pf.to_pandas()

# needed to walk the url request year by year
unix_year = 31556926
# today = int(time.time()) # kinda redundant now that I'm only pulling to end date

# loop over sensors
for index, row in df.iterrows():
    sensor = row['sensor_index']
    created = row['date_created']
    ended = row['last_seen']
    name = row['name']

    print('    ____________','\nSensor: ',name,' (',sensor,')')
    print('Active from ', datetime.fromtimestamp(created).date(),' to ',datetime.fromtimestamp(ended).date())

    # Start at the created date, then pull one year at a time until you hit today
    for x in range(created, ended, unix_year):
        start_timestamp = x
        if (x + unix_year) < ended:
            end_timestamp = x + unix_year
        else:
            end_timestamp = ended

        # construct URL for API pull
        # hist_url = 'https://api.purpleair.com/v1/sensors/' + str(sensor) + '/history?start_timestamp=' + str(start_timestamp) + '&end_timestamp=' + str(end_timestamp) + '&average=1440&fields=pm2.5_alt%2C%20pm2.5_alt_a%2C%20pm2.5_alt_b%2C%20pm2.5_atm%2C%20pm2.5_atm_a%2C%20pm2.5_atm_b%2C%20pm2.5_cf_1%2C%20pm2.5_cf_1_a%2C%20pm2.5_cf_1_b'
        hist_url = 'https://api.purpleair.com/v1/sensors/' + str(sensor) + '/history?start_timestamp=' + str(start_timestamp) + '&end_timestamp=' + str(end_timestamp) + '&average=1440&fields=pm2.5_alt%2C%20pm2.5_atm' # Modified - you don't really need the individual channels but the avg, and ATM & ALT are better for outside than CF_1

        # request from API
        hist_response = requests.get(hist_url, headers=headers)
        print('Pull from ',datetime.fromtimestamp(start_timestamp).date(),' to ',datetime.fromtimestamp(end_timestamp).date(),'| Status code: ', hist_response.status_code)

        try:
            # read hist_response
            hist_content = json.loads(hist_response.content)

            # pull out data & field names
            hist_data = hist_content["data"]
            hist_columns = hist_content["fields"]

            # dump to dataframe
            temp_df = pd.DataFrame(hist_data, columns=hist_columns)

            # add in station_index
            temp_df.insert(0,'station_index',sensor)

            # calculate average
            print('Calculating pm2.5 avg')
            temp_df['pm2.5_AVG'] = (temp_df['pm2.5_alt'] + temp_df['pm2.5_atm']) / 2
            print('Rounding to 1 decimal place')
            temp_df = temp_df.round(1)

            # append to the bottom of hist_df
            hist_df = pd.concat([hist_df, temp_df])

            # dump to parquet
            pw(hist_filename, hist_df, compression='GZIP', append=True)
        except:
            try:
                # read hist_response
                hist_content = json.loads(hist_response.content)

                # pull out data & field names
                hist_data = hist_content["data"]
                hist_columns = hist_content["fields"]

                # dump to dataframe
                temp_df = pd.DataFrame(hist_data, columns=hist_columns)

                # add in station_index
                temp_df.insert(0, 'station_index', sensor)

                # calculate average
                print('Calculating pm2.5 avg')
                temp_df['pm2.5_AVG'] = (temp_df['pm2.5_alt'] + temp_df['pm2.5_atm'])/2
                print('Rounding to 1 decimal place')
                temp_df = temp_df.round(1)

                # append to the bottom of hist_df
                hist_df = pd.concat([hist_df, temp_df])

                # dump to parquet
                pw(hist_filename, hist_df, compression='GZIP', append=True)

            except:
                print(sensor + ": API response failed")

        # API guidelines is hit once every 1-10min, so setting at just over a minute
        sleep(62)

print('Loading ' + hist_filename)
parqf = pf(hist_filename)
hist_df = parqf.to_pandas()

# remove all the duplicate column heading rows (this works ASSUMING that all temp_dfs are exactly the same shape and pull the same data in the same order.  Be careful changing the loop above.
print('De-duplicating')
hist_df = hist_df.drop_duplicates(keep='first')

cleaned_filename = 'data/pa_hist_data_cleaned.parquet'

print('Writing ' + cleaned_filename)
pw(cleaned_filename, hist_df, compression='GZIP')

# remove all the duplicate column heading rows (this works ASSUMING that all temp_dfs are exactly the same shape and pull the same data in the same order.  Be careful changing the loop above.
print('Extracting averages')
avg_df = hist_df[['station_index','time_stamp','pm2.5_AVG']]

avg_filename = 'data/pa_hist_data_avg.parquet'

print('Writing ' + avg_filename)
pw(avg_filename, avg_df, compression='GZIP')