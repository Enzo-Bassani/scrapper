import json
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from tabulate import tabulate


class Stats:
    def __init__(self, avg: float, std: float):
        self.data = {
            'avg': avg,
            'std': std
        }

    def __getitem__(self, index):
        return self.data[index]
    
    def __repr__(self):
        return f'[ Avg: {self['avg']:.2f} | Std: {self.std:.2f} ]'


@dataclass
class BeachStats:
    beach: dict[str]
    stats: dict[str, Stats]
    series: dict[str, pd.Series]

    def __repr__(self):
        headers = ['Attribute', 'Average', 'Std deviation']
        printing_data = [
            ['Rating', self.stats['rating']['avg'], self.stats['rating']['std']],
            ['Temperature', self.stats['temp']['avg'], self.stats['temp']['std']],
            ['Waves Energy', self.stats['wave_energy']['avg'], self.stats['wave_energy']['std']],
            ['Wave Size', self.stats['wave_size']['avg'], self.stats['wave_size']['std']],
            ['Wind Speed', self.stats['wind_speed']['avg'], self.stats['wind_speed']['std']],
        ]

        return f'Name: {self.beach['name']}\n{tabulate(printing_data, headers, tablefmt="grid")}'


state = "Florian\u00f3polis"
time_from = '2024-12-10T06:00:00'
time_to = '2024-12-17T18:00:00'
attribute = 'rating'
stat = 'avg'


def main():

    with open('output.json', 'r') as f:
        data = json.load(f)

    floripa_beaches = [beach for beach in data.values() if beach['state'] == state]

    beaches_stats: list[BeachStats] = []
    for beach in floripa_beaches:

        forecast_items = [(time, info) for time, info in beach['forecast'].items()
                          if time >= time_from and time <= time_to]
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
        beaches_stats.append(beach_stats)

    beaches_stats = sorted(beaches_stats, key=lambda x: x.stats[attribute][stat], reverse=True)

    plt.xlabel('Date')
    plt.ylabel(attribute)
    plt.title(f'{attribute} in top 5 beaches from {state}')
    plt.xticks(rotation=90)
    plt.xlabel('Date', fontsize=12, labelpad=15)
    colors = ['red', 'blue', 'green', 'yellow', 'brown']
    for index, beach_stats in enumerate(beaches_stats[:5]):
        print(beach_stats)
        plt.plot(dates, beach_stats.series[attribute], label=beach_stats.beach['name'], marker='o', color=colors[index])

    
    # Displaying a legend
    plt.legend()

    plt.savefig('Top5_beaches_for_the_week.jpg', dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    main()
