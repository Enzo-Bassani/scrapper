from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import json
from crawler import Crawler
import traceback
import logger
from queue import Queue, ShutDown

search_rotate_value = re.compile(r"rotate\((\-?\d+(\.\d+)?)\)")
time_date_regex = re.compile(r"(?:emitido|issued) (\d{1,2} \w{2}).*(\d{2} \w{3} \d{4})")
state_country_regex = re.compile(r"\(([^,]+)(?:,\s*(.+))?\)")
rating_regex = re.compile(r"^star-rating__rating")


class Scrapper:
    def __init__(self, queue: Queue, output_file_path: str, db, config):
        self.queue = queue
        self.db = db
        self.config = config
        self.config.put(b'finished', b'F')

    def update_output(self, value):
        key = value['url'].encode()
        stored_data_bytes = self.db.get(key)
        if stored_data_bytes:
            stored_data: dict[str] = json.loads(stored_data_bytes)
            stored_data['forecast'].update(value['forecast'])
            value['forecast'] = stored_data['forecast']

        self.db.put(key, json.dumps(value).encode())
        self.config.put(b'lastScrappedURL', key)

    def scrap(self):
        while True:
            try:
                try:
                    break_ = self.queue.get()
                except ShutDown:
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

        self.config.put(b'finished', b'T')

    def __scrap_forecast(self, page: BeautifulSoup, break_entry: dict[str]):
        table = page.find('table', class_="js-forecast-table-content forecast-table__table forecast-table__table--content")

        # Get issued date
        datetime_text = page.find('div', class_='break-header-dynamic__issued').text
        datetime_match = time_date_regex.search(datetime_text)
        time_str, date_str = datetime_match.group(1), datetime_match.group(2)  # e.g., "08 Dec 2024"
        issued_datetime = datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %I %p")

        # Time row
        periods = [period.text for period in table.find('tr', attrs={"data-row-name": "time"}).find_all('td')]
        datetimes = []
        curr_datetime = issued_datetime
        for period in periods:
            advance_day = False
            match period:
                case 'manhã' | 'AM':
                    curr_datetime = curr_datetime.replace(hour=6)
                case 'tarde' | 'PM':
                    curr_datetime = curr_datetime.replace(hour=12)
                case 'noite' | 'Night':
                    curr_datetime = curr_datetime.replace(hour=18)
                    advance_day = True
                case _:
                    raise Exception("Unidentified time")

            datetimes.append(curr_datetime.isoformat())
            if advance_day:
                curr_datetime += timedelta(days=1)


        
        # Wave(m) row
        wave_row = table.find('tr', attrs={"data-row-name": "wave-height"})
        wave_info_by_date = [wave_info.div for wave_info in wave_row.find_all('td')]
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


        # Avaliação row
        rating_row = table.find('tr', attrs={"data-row-name": "rating"})
        ratings_info_by_date = [rating.find('div', class_=rating_regex) for rating in rating_row.find_all('td')]
        for entry, rating_info in zip(entries, ratings_info_by_date):
            rating = int(rating_info.text) if rating_info is not None else 0
            entry['rating'] = rating

        # Período (s) row
        periods_row = table.find('tr', attrs={"data-row-name": "periods"})
        periodo_by_date = periods_row.find_all('td')
        for entry, periodo in zip(entries, periodo_by_date):
            periodo_text = periodo.text.strip()
            entry['periodo'] = periodo_text if periodo_text == '-' else int(periodo_text)

        # Energy. row
        energy_row = table.find('tr', attrs={"data-row-name": "energy"})
        energy_by_time = [int(energy.text) for energy in energy_row.find_all('td')]
        for entry, energy in zip(entries, energy_by_time):
            entry['energy'] = energy

        # Vento(km/h) row
        wind_row = table.find('tr', attrs={"data-row-name": "wind"})
        wind_by_date = wind_row.find_all('td')
        for entry, wind_info in zip(entries, wind_by_date):
            scrapped = {
                'wind_degrees': float(search_rotate_value.search(wind_info.div.svg.g['transform']).group(1)),
                'wind_speed': float(wind_info.div.svg.find('text').text)
            }
            entry.update(scrapped)

        # Estado do vento row
        wind_state_row = table.find('tr', attrs={"data-row-name": "wind-state"})
        estados_by_time = [estado.text for estado in wind_state_row.find_all('td')]
        for entry, estado in zip(entries, estados_by_time):
            entry['wind_state'] = estado

        # Temp. row
        temperature_row = table.find('tr', attrs={"data-row-name": "temperature-high"})
        temp_by_time = [int(temp.text) for temp in temperature_row.find_all('td')]
        for entry, temp in zip(entries, temp_by_time):
            entry['temp'] = temp

        # Feels. row
        feels_row = table.find('tr', attrs={"data-row-name": "feels"})
        feels_by_time = [int(feels.text) for feels in feels_row.find_all('td')]
        for entry, feels in zip(entries, feels_by_time):
            entry['feels'] = feels

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
        entry['state'] = state
        entry['country'] = country
        entry['type'] = type.text
        entry['rating'] = float(rating.span.text)
        entry['reliability'] = reliability.text
