# Center for Equitable Policy in a Changing World
## wildfire-smoke

### Project Description:
Project studying the geography of wildfire smoke in the Puget Sound region.

#### Filelist
- _data_clean.py_:
  - This file expects to find a list of csvs in /data/raw that have at least two columns: 'Observation Time' and some number of data columns (i.e. 'Seattle Duwamish Vly - Pm25MetOneBam - ug/m3 - 24Hr Avg').  We have omitted these to save space. It first strips the comments from the top of the file, placing the cleaned versions in /data/cleaned, and then combines them into an aggregated dataset (_aqi_data.csv_) in /data.
- _/data/aqi_data.csv_:
  - resulting aggregated dataset produced by _data_clean.py_

### Data source
We're starting with an initial dataset of AQI data from the [Puget Sound Clean Air Agency](https://pscleanair.gov/154/Air-Quality-Data).


### Principal researchers
Richard W. Sharp\
Patrick W. Zimmerman

#### Codebase
**Data prep**: Python 3.10

#### Python Package requirements (as well as all their dependencies)
csv\
os\
pandas
