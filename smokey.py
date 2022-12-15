import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/aqi_data_stacked.csv')

print('loading dataframe')
df['Observation Time'] = pd.to_datetime(df['Observation Time'])

fig, ax = plt.subplots(figsize=(30,16))

ax.set(xlabel='Time', ylabel='AQI')
print('drawing graph: AQI')
sns.lineplot(x='Observation Time', y='value', hue='measure',data=df)

plt.title('Puget Sound Air Quality Index over time')

plt.savefig('AQI.png')

fig, ax = plt.subplots(figsize=(30,16))

ax.set_yscale('log')
ax.set(xlabel='Time', ylabel='AQI')
print('drawing graph: AQI (log scale)')
sns.lineplot(x='Observation Time', y='value', hue='measure',data=df)

plt.title('Puget Sound Air Quality Index over time (log scale)')

plt.savefig('AQI_log.png')

df150 = df[(df['value'] >= 150)] #select for days where schools will close

fig, ax = plt.subplots(figsize=(30,16))

ax.set(xlabel='Time', ylabel='AQI')
print('drawing graph: AQI 150+')
sns.scatterplot(x='Observation Time', y='value', hue='measure',data=df150, s=10)

plt.title('Puget Sound Air Quality Index: days 150+')

plt.savefig('AQI_150.png')

df100 = df[(df['value'] >= 100)] #select for days with unhealthy air

fig, ax = plt.subplots(figsize=(30,16))

ax.set(xlabel='Time', ylabel='AQI')
print('drawing graph: AQI 100+')
sns.scatterplot(x='Observation Time', y='value', hue='measure',data=df100, s=100)

plt.title('Puget Sound Air Quality Index: days 100+')

plt.savefig('AQI_100.png')