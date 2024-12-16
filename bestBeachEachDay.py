import json
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from tabulate import tabulate

state = "Florian\u00f3polis"
time_from = '2024-12-10T06:00:00'
time_to = '2024-12-17T18:00:00'
attribute = 'rating'

with open('output.json', 'r') as f:
    data = json.load(f)

floripa_beaches = [beach for beach in data.values() if beach['state'] == state]
dates = floripa_beaches[0]['forecast'].keys()
dates = sorted(dates)

best_by_date = []
for date in dates:
    best = max(floripa_beaches, key=lambda beach: beach['forecast'][date][attribute])
    best_by_date.append(best)

headers = ['Date', 'Best Beach', attribute]
printing_data = []
for date, beach in zip(dates, best_by_date):
    printing_data.append([date, beach['name'], beach['forecast'][date][attribute]])
print(tabulate(printing_data, headers, tablefmt="grid"))