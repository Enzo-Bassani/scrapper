import json
import pandas as pd
import matplotlib.pyplot as plt

with open('output.json', 'r') as f:
    data = json.load(f)

malibu = data['https://pt.surf-forecast.com/breaks/Malibu_3']
time_from = '2024-12-10T06:00:00'
time_to = '2024-12-17T18:00:00'

forecast_items = [(time, info) for time, info in malibu['forecast'].items() if time >= time_from and time <= time_to]
forecast_items = sorted(forecast_items, key=lambda x: x[0])
dates = [x[0][5:13] for x in forecast_items]
forecast_array = [x[1] for x in forecast_items]

temp_series = pd.Series([info['temp'] for info in forecast_array])
energy_series = pd.Series([info['energy'] for info in forecast_array])
wave_size_series = pd.Series([info['wave_size'] for info in forecast_array])
wind_speed_series = pd.Series([info['wind_speed'] for info in forecast_array])

print("Temperature average: ", temp_series.mean())
print("Temperature std: ", temp_series.std())

print("Energy average: ", energy_series.mean())
print("Energy std: ", energy_series.std())

print("Wave size average: ", wave_size_series.mean())
print("Wave size std: ", wave_size_series.std())

print("Wind speed average: ", wind_speed_series.mean())
print("Wind speed std: ", wind_speed_series.std())


plt.plot(dates, energy_series, label='energy_series', marker='o', color='blue')
plt.xlabel('Month')
plt.ylabel('Amount ($)')
plt.title('Waves energy in Malibu')
plt.xticks(rotation=90)
plt.xlabel('Date', fontsize=12, labelpad=15)

plt.show()
