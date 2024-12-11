from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import json
from crawler import Crawler
import traceback
import logger

search_rotate_value = re.compile(r"rotate\((\-?\d+(\.\d+)?)\)")
time_date_regex = re.compile(r"emitido (\d{1,2} \w{2}).*(\d{2} \w{3} \d{4})")
state_country_regex = re.compile(r"\(([^,]+),\s*(\w+)\)")


class Scrapper:
    def __init__(self, crawler: Crawler, output_file_path: str, db):
        self.crawler = crawler
        self.db = db

    def update_output(self, value):
        key = value['url'].encode()
        stored_data_bytes = self.db.get(key)
        if stored_data_bytes:
            stored_data: dict[str] = json.loads(stored_data_bytes)
            stored_data['forecast'].update(value['forecast'])
            value['forecast'] = stored_data['forecast']

        self.db.put(key, json.dumps(value).encode())

    def scrap(self):
        while True:
            try:
                break_, empty = self.crawler.pop()
                if empty:
                    break

                main_page = BeautifulSoup(break_.main_page, 'html.parser')
                forecast_page = BeautifulSoup(break_.forecast_page, 'html.parser')
                entry = {}

                logger.logger.info(f'Scrapping {break_.url}')
                entry['url'] = break_.url

                ###### GUIDE HEADER ######
                self.__scrap_guide_header(main_page, entry)

                ###### FORECAST ######
                self.__scrap_forecast(forecast_page, entry)

                self.update_output(entry)
                logger.logger.info(json.dumps(entry, indent=4))

            except Exception as e:
                logger.logger.error(traceback.format_exc())

    def __scrap_forecast(self, page: BeautifulSoup, break_entry: dict[str]):
        table = page.find('table').find_all('tr')

        # Get issued date
        datetime_text = page.find('div', class_='break-header-dynamic__issued').text
        datetime_match = time_date_regex.search(datetime_text)
        time_str, date_str = datetime_match.group(1), datetime_match.group(2)  # e.g., "08 Dec 2024"
        issued_datetime = datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %I %p")

        # Time row
        periods = [period.text for period in page.find('table').find('tr', attrs={"data-row-name": "time"}).find_all('td')]
        datetimes = []
        curr_datetime = issued_datetime
        for period in periods:
            advance_day = False
            match period:
                case 'manhã':
                    curr_datetime = curr_datetime.replace(hour=6)
                case 'tarde':
                    curr_datetime = curr_datetime.replace(hour=12)
                case 'noite':
                    curr_datetime = curr_datetime.replace(hour=18)
                    advance_day = True

            datetimes.append(curr_datetime.isoformat())
            if advance_day:
                curr_datetime += timedelta(days=1)

        # Wave(m) row
        wave_info_by_date = [wave_info.div for wave_info in table[4].find_all('td')]
        entries = [{} for _ in range(len(wave_info_by_date))]
        for entry, wave_info in zip(entries, wave_info_by_date):
            if wave_info is None:
                scrapped = {'wave_cardinal_direction': '-', 'wave_degrees': '-', 'wave_size': '-'}
            else:
                scrapped = {
                    'wave_cardinal_direction': wave_info.div.text,
                    'wave_degrees': float(search_rotate_value.search(wave_info.svg.g['transform']).group(1)),
                    'wave_size': float(wave_info.svg.find('text').text)
                }
            entry.update(scrapped)

        # Período (s) row
        periodo_by_date = table[5].find_all('td')
        for entry, periodo in zip(entries, periodo_by_date):
            periodo_text = periodo.text.strip()
            entry['periodo'] = periodo_text if periodo_text == '-' else int(periodo_text)

        # Energy. row
        energy_by_time = [energy.text for energy in table[7].find_all('td')]
        for entry, energy in zip(entries, energy_by_time):
            entry['energy'] = int(energy)

        # Vento(km/h) row
        wind_by_date = table[8].find_all('td')
        for entry, wind_info in zip(entries, wind_by_date):
            scrapped = {
                'wind_degrees': float(search_rotate_value.search(wind_info.div.svg.g['transform']).group(1)),
                'wind_speed': float(wind_info.div.svg.find('text').text)
            }
            entry.update(scrapped)

        # Estado do vento row
        estados_by_time = [estado.text for estado in table[9].find_all('td')]
        for entry, estado in zip(entries, estados_by_time):
            entry['wind_state'] = estado

        # Temp. row
        temp_by_time = [temp.text for temp in table[18].find_all('td')]
        for entry, temp in zip(entries, temp_by_time):
            entry['temp'] = int(temp)

        # Feels. row
        feels_by_time = [feels.text for feels in table[19].find_all('td')]
        for entry, feels in zip(entries, feels_by_time):
            entry['feels'] = int(feels)

        break_entry['forecast'] = {}
        for time, forecast_entry in zip(datetimes, entries):
            break_entry['forecast'][time] = forecast_entry

    def __scrap_guide_header(self, page: BeautifulSoup, entry: dict[str]):
        guide_header = page.find('div', class_='guide-header__spotid')
        table = guide_header.find('table', class_='guide-header__information').find_all('tbody')

        type, rating = table[0].tr.find_all('td')
        reliability, temperature = table[1].tr.find_all('td')

        state_country_text = page.find('h2', class_='h1add tab').text
        match = state_country_regex.search(state_country_text)

        state, country = match.group(1), match.group(2)

        entry['name'] = guide_header.find('h2').find('b').text
        entry['state'] =  state
        entry['country'] = country
        entry['type'] = type.text
        entry['rating'] = int(rating.span.text)
        entry['reliability'] = reliability.text
        entry['temperature'] = float(temperature.div.span.text)
