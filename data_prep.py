import numpy as np
import pandas as pd
from datetime import datetime
from fastparquet import ParquetFile as pf
from fastparquet import write as pw
# import seaborn as sns
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import geoplot as gplt
import matplotlib.pyplot as plt
import matplotlib
import cartopy.crs as ccrs
import csv

filename = 'data/pa_hist_data_avg.parquet'
station_filename = 'data/pa_station_list.csv'
geo_filename = 'data/washingtongeo.json'

print('Loading ' + filename + ' & ' + station_filename)
parqf = pf(filename)
df = parqf.to_pandas()
df_stations = pd.read_csv(station_filename)

df_stations_temp = df_stations[['sensor_index','name','latitude','longitude','altitude']]
df_stations_temp = df_stations_temp.rename(columns={"sensor_index": "station_index"})
df_temp = df[['station_index','time_stamp','pm2.5_AVG']]
df_temp = df_temp.rename(columns={"pm2.5_AVG": "pm2_5_AVG"}) # this is so D3 doesn't go nuts on the decimal point
df_temp = df_temp[(df_temp['time_stamp'] > 1672592400) & (df_temp['time_stamp'] < 1672642800)].drop_duplicates()

# spit out merged datafile for d3, which does not like parquet
d3_df = df_temp.merge(df_stations_temp, left_on='station_index', right_on='station_index')
d3_filename = 'map/stations.csv'
d3_df.to_csv(d3_filename, index=False, quotechar='"', quoting=csv.QUOTE_ALL)

# wa_shp = gpd.read_file(geo_filename)
# wa_select_counties = wa_shp[wa_shp['COUNTYFP'].isin(['009','029','031','033','035','045','053','055','057','061','067','073'])] # select only counties within Puget Sound south of Pt Townsend
#
# df_stations['geometry'] = gpd.points_from_xy(df_stations['longitude'], df_stations['latitude'])
#
# ax = gplt.polyplot(
#     wa_select_counties, projection=gcrs.AlbersEqualArea(),
#     edgecolor='None', facecolor='#f6f0e8',
#     figsize=(20,30)
# )
#
# fig = gplt.pointplot(
#     gpd.GeoDataFrame(df_stations[df_stations['pm2.5_24hour'].notnull()]), s=10,
#     hue='pm2.5_24hour', ax=ax, legend=True
# )
# plt.title('24_hour AQI (as of Jan 2023)')
#
# plt.savefig('AQI_map.png')
#
# plt.show()

# Bounding box
max_lat = 48
min_lon = -123
min_lat = 47
max_lon = -122

# plot_col = 'pm2.5_24hour'
# plot_data = df_stations[df_stations[plot_col].notnull()]
#
# norm = matplotlib.colors.Normalize(vmin=0, vmax=np.percentile(plot_data[plot_col],97))
#
# ax = wa_select_counties.plot(
#     figsize=(20,30),
#     facecolor='#f6f0e8',
#     edgecolor='black'
# )
#
# gplt.pointplot(
#     gpd.GeoDataFrame(plot_data),
#     s=10,
#     hue='pm2.5_24hour',
#     cmap='RdYlGn_r',
#     ax=ax,
#     legend=True,
#     norm=norm
# )
#
# ccrs.PlateCarree()
#
# seattle_contours = gpd.read_file('data/shape/Elev_Contour.shp')
#
# # with open('map/seattle_contours.geojson', 'w') as file:
# #     file.write(seattle_contours.to_json()) # use mapshaper.org instead - this is easier and you can simplify it rather than mess wit the CLI
#
# seattle_contours.plot(ax=ax, alpha=0.1)
#
# plt.title('24_hour AQI (as of Jan 2023)')
#
# ax.set_xlim((min_lon,max_lon))
# ax.set_ylim((min_lat,max_lat))
#
# plt.savefig('AQI_map_contour.png')
# plt.show()