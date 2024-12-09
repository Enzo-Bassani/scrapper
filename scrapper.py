from bs4 import BeautifulSoup
import re
import json
from crawler import Crawler
from requestsHandler import RequestsHandler
import threading
import traceback
import logger
import sys
import os

search_rotate_value = re.compile(r"rotate\((\-?\d+(\.\d+)?)\)")


class Scrapper:
    def __init__(self, crawler: Crawler, output_file_path: str):
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        self.output_file = open(output_file_path, 'a')
        self.output_file.write("[\n")

        self.crawler = crawler

    def append_output(self, value):
        json.dump(value, self.output_file, indent=4)
        self.output_file.write(',\n')

    def close_output(self):
        self.output_file.write('\n]')
        self.output_file.close()

    def scrap(self):
        response = []

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

                ###### BASIC FORECAST ######
                self.__scrap_basic_forecast(main_page, entry)

                ###### FORECAST ######
                # self.__scrap_forecast(forecast_page, entry)

                self.append_output(entry)
                logger.logger.info(json.dumps(entry, indent=4))
                response.append(entry)

            except Exception as e:
                logger.error(traceback.format_exc())

        self.close_output()
        return response
    
    # def __scrap_forecast(self, page: BeautifulSoup, entry: dict[str]):
    #     table = page.find('div', class_=['forecast-table__scroll-container']).table.find_all('tr')
        


    #     times = [entry.text for entry in table[1].find_all('td')]

    #     # Wave(m) row
    #     wave_info_by_time = [wave_info.div for wave_info in table[2].find_all('td')]
    #     entry['wave'] = {}
    #     for time, wave_info in zip(times, wave_info_by_time):
    #         if wave_info is None:
    #             entry['wave'][time] = {'cardinal_direction': '-', 'degrees': '-', 'size': '-'}
    #             continue

    #         entry['wave'][time] = {
    #             'cardinal_direction': wave_info.div.text,
    #             'degrees': float(search_rotate_value.search(wave_info.svg.g['transform']).group(1)),
    #             'size': float(wave_info.svg.find('text').text)
    #         }

    #     # Período (s) row
    #     periodos_by_time = []
    #     for periodo in table[3].find_all('td'):
    #         periodo_text = periodo.text.strip()
    #         periodos_by_time.append(periodo_text if periodo_text == '-' else int(periodo_text))
    #     entry['periodo'] = {}
    #     for time, periodo in zip(times, periodos_by_time):
    #         entry['periodo'][time] = periodo

    #     # Vento(km/h) row
    #     wind_by_time = table[4].find_all('td')
    #     entry['wind'] = {}
    #     for time, wind_info in zip(times, wind_by_time):
    #         entry['wind'][time] = {
    #             'degrees': float(search_rotate_value.search(wind_info.div.svg.g['transform']).group(1)),
    #             'speed': float(wind_info.div.svg.find('text').text)
    #         }

    #     # Estado do vento row
    #     estados_by_time = [estado.text for estado in table[5].find_all('td')]
    #     entry['estado'] = {}
    #     for time, estado in zip(times, estados_by_time):
    #         entry['estado'][time] = estado




    def __scrap_guide_header(self, page: BeautifulSoup, entry: dict[str]):
        guide_header = page.find('div', class_='guide-header__spotid')
        table = guide_header.find('table', class_='guide-header__information').find_all('tbody')

        type, rating = table[0].tr.find_all('td')
        reliability, temperature = table[1].tr.find_all('td')

        entry['name'] = guide_header.find('h2').find('b').text
        entry['type'] = type.text
        entry['rating'] = int(rating.span.text)
        entry['reliability'] = reliability.text
        entry['temperature'] = float(temperature.div.span.text)

    def __scrap_basic_forecast(self, page: BeautifulSoup, entry: dict[str]):
        table = page.find('div', class_=['forecast_upcoming forecast_upcoming--newhead',
                            'forecast-cta__current-forecast', 'forecasts forecast-cta']).table.find_all('tr')

        times = [entry.text for entry in table[1].find_all('td')]

        # Wave(m) row
        wave_info_by_time = [wave_info.div for wave_info in table[2].find_all('td')]
        entry['wave'] = {}
        for time, wave_info in zip(times, wave_info_by_time):
            if wave_info is None:
                entry['wave'][time] = {'cardinal_direction': '-', 'degrees': '-', 'size': '-'}
                continue

            entry['wave'][time] = {
                'cardinal_direction': wave_info.div.text,
                'degrees': float(search_rotate_value.search(wave_info.svg.g['transform']).group(1)),
                'size': float(wave_info.svg.find('text').text)
            }

        # Período (s) row
        periodos_by_time = []
        for periodo in table[3].find_all('td'):
            periodo_text = periodo.text.strip()
            periodos_by_time.append(periodo_text if periodo_text == '-' else int(periodo_text))
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

