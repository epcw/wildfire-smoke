import pandas as pd
from datetime import datetime
from time import sleep
from fastparquet import ParquetFile as pf
from fastparquet import write as pw
import seaborn as sns
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import geoplot as gplt
import geoplot.crs as gcrs
import matplotlib.pyplot as plt


filename = 'data/pa_hist_data_avg.parquet'
station_filename = 'data/pa_station_list.csv'
geo_filename = 'data/washingtongeo.json'

print('Loading ' + filename + ' & ' + station_filename)
parqf = pf(filename)
df = parqf.to_pandas()
df_stations = pd.read_csv(station_filename)

wa_shp = gpd.read_file(geo_filename)
wa_select_counties = wa_shp[wa_shp['COUNTYFP'].isin(['009','029','031','033','035','045','053','055','057','061','067','073'])]

df_stations['geometry'] = gpd.points_from_xy(df_stations['longitude'], df_stations['latitude'])

ax = gplt.polyplot(
    wa_select_counties, projection=gcrs.AlbersEqualArea(),
    edgecolor='None', facecolor='#f6f0e8',
    figsize=(20,30)
)

fig = gplt.pointplot(
    gpd.GeoDataFrame(df_stations[df_stations['pm2.5_24hour'].notnull()]), s=10,
    hue='pm2.5_24hour', ax=ax, legend=True
)
plt.title('24_hour AQI (as of Jan 2023)')

plt.savefig('AQI_map.png')

plt.show()