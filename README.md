# Center for Equitable Policy in a Changing World
## wildfire-smoke

### Project Description:
Project studying the geography of wildfire smoke in the Puget Sound region.

#### Filelist
- _data_clean.py_:
  - This file expects to find a list of csvs in /data/raw that have at least two columns: 'Observation Time' and some number of data columns (i.e. 'Seattle Duwamish Vly - Pm25MetOneBam - ug/m3 - 24Hr Avg').  We have omitted these to save space. It first strips the comments from the top of the file, placing the cleaned versions in /data/cleaned, and then combines them into an aggregated dataset (_aqi_data.csv_) in /data.
- _smokey.py_:
  - Produces line and scatter plots of Clean Are Agency AQI data, using _/data/aqi_data_stacked.csv_ as a required input.  
- _AQI.png_, _AQI_100.png_, _AQI_150.png_, _AQI_log.png_:
  - output graphs produced by _smokey.py_
- _/data/aqi_data.csv_:
  - Aggregated datafile produced by _data_clean.py_. _NOT INCLUDED IN REPO_ for size reasons.
- _/data/aqi_data_stacked.csv_:
  - Disaggregated datafile produced by _data_clean.py_. _NOT INCLUDED IN REPO_ for size reasons.
- _/data/pa_hist_data.csv_,_pa_data_cleaned.parquet_,_pa_hist_data_avg.parquet_:
  - Datafiles produced by _purpleair_fetch.py_. _NOT INCLUDED IN REPO_ for size reasons.
- _/data/shape/_:
  - Directory with all the elevation shapefiles. _NOT INCLUDED IN REPO_ for size reasons.
- _purpleair_fetch.py_:
  - Fetches list of stations from PurpleAir within Puget Sound and pulls historical data, saving as _pa_hist_data_avg.parquet_
- _api_key_sample.txt_:
  - Required input for _purpleair_fetch.py_ Your PurpleAir API GET key goes here in the first line, just raw text, no wrappers.
- _data_prep.py_:
  - Produces map of Purple Air AQI data, using _/data/pa_hist_data_avg.parquet_ and _data/shape/Elev_Contour.shp_ as required inputs.  
- _AQI_map_contour.png_:
  - output map produced by _data_prep.py_
- _index.html_:
  - Webpage for viz goes here.
- _/map/_:
  - Directory with all the vizualization pieces.
- _/map/aqi.js_:
  - d3 script that creates the vizualization
- _/map/aqi.css_:
  - css to style the map and index page.
- _/map/filtered_seattle_contours.json_:
  - contour map file.  Created with the shapefiles above in [mapshaper.org](https://mapshaper.org/) and exported as a topoJson.  _NOT INCLUDED IN REPO_ for size reasons.
- _/map/jquery.3.5.1.min.js_:
  - need to host jquery for page interactivity.  Or you could probably import it in the html file, but this works, too.
- _/map/stations.csv_:
  - data source for the stations to be used in the map (derived from _pa_hist_data_avg.parquet_).  _NOT INCLUDED IN REPO_ for size reasons.

### Data source
We're starting with an initial dataset of AQI data from the [Puget Sound Clean Air Agency](https://pscleanair.gov/154/Air-Quality-Data) and combining it with a historical scrape of public Purple Air stations ([API reference](https://api.purpleair.com/#api-sensors-get-sensor-history)) from 2017-onwards.  Elevation contour files are from the USGS's [National Map](https://www.sciencebase.gov/catalog/item/4f70ab22e4b058caae3f8deb).

### Principal researchers
Richard W. Sharp\
Patrick W. Zimmerman

#### Codebase
**Data prep & initial analysis**: Python 3.10\
**Vizualization**: D3.js v4

#### Python Package requirements (as well as all their dependencies)
csv\
os\
pandas\
seaborn\
matplotlib\
fastparquet\
numpy\
datetime\
geopandas\
geoplot\
cartopy

#### Javascript libraries to import in _index.html_
d3.v4\
d3-contour\
d3-delaunay\
topojson
