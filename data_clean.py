import os
import pandas as pd
import csv

files = 'data/raw'
cleanfiles = 'data/cleaned'

# RAW FILE INPUT AND CLEANING COMMENTS
for filename in os.listdir(files):
    f = os.path.join(files, filename)

    with open(f) as file:
        lines = file.readlines()

    lines = lines[8:]

    fout = os.path.join(cleanfiles, filename)

    with open(fout, "w+") as output: # save on new_file
        output.writelines(lines)

    print('cleaning ' + filename)

# COMBINE INTO SINGLE FILE AND DATAFRAME
# set empty df and create index column
df = pd.DataFrame(columns=['Observation Time'])

# loop over data directory and merge all the resulting csvs into df
for filename in os.listdir(cleanfiles):
    f = os.path.join(cleanfiles, filename)

    with open(f, "r") as file:
        filename = pd.read_csv(file)
        df = df.merge(filename, how="outer",  left_on=['Observation Time'], right_on=['Observation Time']
                      )

# keep only the '_x' suffix columns if there are repeats. There will LIKELY be repeats, as some unknown number of the station groups have overlapping stations / measures
df.columns = df.columns.str.replace("_x", "")
df = df[df.columns.drop(list(df.filter(regex='_y$')))]

# drop duplicate columns and rows
df = df.loc[:,~df.columns.duplicated()]
df = df.drop_duplicates(keep='first')

# convert observation time to datetime and sort ascending
df['Observation Time'] = pd.to_datetime(df['Observation Time'])
df = df.sort_values(by=['Observation Time'])

# drop rows with no data at all other than Observation Time
dfheaders = df.columns.values.tolist()
dfheaders = dfheaders[1:]
df.dropna(how='all', subset=dfheaders, inplace=True)

df_filename = 'data/aqi_data.csv'

print("exporting " + df_filename)
df.to_csv(df_filename, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
