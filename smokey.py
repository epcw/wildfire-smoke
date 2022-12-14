import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/aqi_data_stacked.csv')

print('loading dataframe')
df['Observation Time'] = pd.to_datetime(df['Observation Time'])

fig, ax = plt.subplots(figsize=(16,10))
print('drawing graph')
sns.lineplot(x='Observation Time', y='value', hue='measure',data=df)

plt.title('AQI')

# x = df['Observation Time']
# y = df['value']

# for index in range(len(x)):
#     ax.text(x[index],y[index], size=7)

# plt.show()
plt.savefig('AQI.png')
