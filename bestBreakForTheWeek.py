import json
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class Stats:
    avg: float
    std: float

    def __repr__(self):
        # Custom string representation for the dataclass
        return f'[ Avg: {self.avg} | Std: {self.std}'


@dataclass
class BeachStats:
    beach_name: str
    rating: Stats
    temp: Stats
    waves_energy: Stats
    wave_size: Stats
    wind_speed: Stats

    def __repr__(self):
        # Custom string representation for the dataclass
        return f'''Name: {self.beach_name}
Rating: {self.rating}
Temp: {self.temp}
Waves Energy: {self.waves_energy}
Wave Size: {self.wave_size}
Wind Speed: {self.wind_speed}        
'''
         


state = "Florian\u00f3polis"
time_from = '2024-12-10T06:00:00'
time_to = '2024-12-17T18:00:00'

with open('output.json', 'r') as f:
    data = json.load(f)

floripa_beaches = [beach for beach in data.values() if beach['state'] == state]

beaches_stats: list[BeachStats] = []
for beach in floripa_beaches:

    forecast_items = [(time, info) for time, info in beach['forecast'].items() if time >= time_from and time <= time_to]
    # forecast_items = sorted(forecast_items, key=lambda x: x[0])
    dates = [x[0][5:13] for x in forecast_items]
    forecast_array = [x[1] for x in forecast_items]

    rating_series = pd.Series([info['rating'] for info in forecast_array])
    temp_series = pd.Series([info['temp'] for info in forecast_array])
    energy_series = pd.Series([info['energy'] for info in forecast_array])
    wave_size_series = pd.Series([info['wave_size'] for info in forecast_array])
    wind_speed_series = pd.Series([info['wind_speed'] for info in forecast_array])

    rating_stats = Stats(rating_series.mean(), rating_series.std())
    temp_stats = Stats(temp_series.mean(), temp_series.std())
    energy_stats = Stats(energy_series.mean(), energy_series.std())
    wave_size_stats = Stats(wave_size_series.mean(), wave_size_series.std())
    wind_speed_stats = Stats(wind_speed_series.mean(), wind_speed_series.std())

    beach_stats = BeachStats(beach['name'], rating_stats, temp_stats, wave_size_stats, wave_size_stats, wind_speed_stats)
    beaches_stats.append(beach_stats)

beaches_stats = sorted(beaches_stats, key=lambda x: x.rating.avg, reverse=True)

for beach_stats in beaches_stats[:5]:
    print(beach_stats)
