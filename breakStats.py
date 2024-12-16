import json
import pandas as pd
import matplotlib.pyplot as plt
from bestBeachForTheWeek import Stats, BeachStats

beach_url = 'https://pt.surf-forecast.com/breaks/Abacateiro'
time_from = '2024-12-10T06:00:00'
time_to = '2024-12-17T18:00:00'


def main():
    with open('output.json', 'r') as f:
        data = json.load(f)

    beach = data[beach_url]
    forecast_items = [(time, info) for time, info in beach['forecast'].items() if time >= time_from and time <= time_to]
    dates = [x[0][5:13] for x in forecast_items]
    forecast_array = [x[1] for x in forecast_items]

    series = {
        'rating': pd.Series([info['rating'] for info in forecast_array]),
        'temp': pd.Series([info['temp'] for info in forecast_array]),
        'wave_energy': pd.Series([info['energy'] for info in forecast_array]),
        'wave_size': pd.Series([info['wave_size'] for info in forecast_array]),
        'wind_speed': pd.Series([info['wind_speed'] for info in forecast_array])
    }

    stats = {
        'rating': Stats(series['rating'].mean(), series['rating'].std()),
        'temp': Stats(series['temp'].mean(), series['temp'].std()),
        'wave_energy': Stats(series['wave_energy'].mean(), series['wave_energy'].std()),
        'wave_size': Stats(series['wave_size'].mean(), series['wave_size'].std()),
        'wind_speed': Stats(series['wind_speed'].mean(), series['wind_speed'].std())
    }

    beach_stats = BeachStats(beach, stats, series)

    print(beach_stats)

    plt.plot(dates, beach_stats.series['wave_energy'], label='energy_series', marker='o', color='blue')
    plt.xlabel('Date')
    plt.ylabel('Energy')
    plt.title(f'Waves energy in {beach['name']}')
    plt.xticks(rotation=90)
    plt.xlabel('Date', fontsize=12, labelpad=15)

    plt.savefig('wave_energy_graph.jpg', dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    main()
