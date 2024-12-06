from bs4 import BeautifulSoup
import re
import json
from requestsHandler import RequestsHandler


search_rotate_value = re.compile(r"rotate\((\d+(\.\d+)?)\)")

beaches_links = ['https://pt.surf-forecast.com/breaks/Barra-da-Lagoa'] * 10

info = []

for link in beaches_links:
    response = RequestsHandler.get(link)
    page = BeautifulSoup(response, 'html.parser')
    print(page)
    entry = {}

    ##########################
    ###### GUIDE HEADER ######
    ##########################

    guide_header = page.find('div', class_='guide-header__spotid')
    table = guide_header.find('table', class_='guide-header__information').find_all('tbody')

    type, rating = table[0].tr.find_all('td')
    reliability, temperature = table[1].tr.find_all('td')

    entry['name'] = guide_header.find('h2').find('b').text
    entry['type'] = type.text
    entry['rating'] = int(rating.span.text)
    entry['reliability'] = reliability.text
    entry['temperature'] = float(temperature.div.span.text)

    ###############################
    ###### forecast_upcoming ######
    ###############################

    table = page.find('div', class_='forecast_upcoming forecast_upcoming--newhead').table.find_all('tr')

    times = [entry.text for entry in table[1].find_all('td')]

    # Wave(m) row
    wave_info_by_time = table[2].find_all('td')
    entry['wave'] = {}
    for time, wave_info in zip(times, wave_info_by_time):
        entry['wave'][time] = {
            'cardinal_direction': wave_info.div.div.text,
            'degrees': float(search_rotate_value.search(wave_info.div.svg.g['transform']).group(1)),
            'size': float(wave_info.div.svg.find('text').text)
        }

    # Período (s) row
    periodos_by_time = [int(periodo.text.strip()) for periodo in table[3].find_all('td')]
    entry['periodo'] = {}
    for time, periodo in zip(times, periodos_by_time):
        entry['periodo'][time] = periodo

    # Vento(km/h) row
    wind_by_time = table[4].find_all('td')
    entry['wind'] = {}
    for time, wind_info in zip(times, wind_by_time):
        entry['wind'][time] = {
            'degrees': float(search_rotate_value.search(wind_info.div.svg.g['transform']).group(1)),
            'speed': float(wind_info.div.svg.find('text').text)
        }

    # Estado do vento row
    estados_by_time = [estado.text for estado in table[5].find_all('td')]
    entry['estado'] = {}
    for time, estado in zip(times, estados_by_time):
        entry['estado'][time] = estado

    print(json.dumps(entry, indent=4))
    info.append(entry)
