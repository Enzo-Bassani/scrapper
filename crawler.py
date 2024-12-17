from dataclasses import dataclass
from queue import Queue, ShutDown
from bs4 import BeautifulSoup
import re
from requestsHandler import RequestsHandler
import threading
import logger

a_lot = 2**32
host = 'pt.surf-forecast.com'


@dataclass
class Break:
    main_page: str
    forecast_page: str
    url: str


class Crawler:
    def __init__(self, output_buffer: Queue[Break], limit, config) -> None:
        self.countries_url = 'https://www.surf-forecast.com/countries'
        self.breaks_URLs_queue: list[str] = []

        self.output_buffer = output_buffer

        self.config = config

        self.continueFrom = ''
        finished = self.config.get(b'finished')
        if finished == b'F':
            self.continueFrom = self.config.get(b'lastScrappedURL').decode()

        self.limit = limit

    def crawl(self):
        threading.Thread(target=self.__crawl).start()

    def __crawl(self):
        starting_page_real = BeautifulSoup(RequestsHandler.get(self.countries_url), 'html.parser')

        countries_page_links = starting_page_real.find('table').find_all('a', href=re.compile('^/countries/'))
        countries_links = [self.__get_full_url(host, link) for link in countries_page_links]

        count = 0
        for country_link in countries_links:
            country_page = BeautifulSoup(RequestsHandler.get(country_link), 'html.parser')

            country_page_links = country_page.find('table').find_all('a', href=re.compile('^/breaks/'))
            breaks_links = [self.__get_full_url(host, link) for link in country_page_links]

            for break_link in breaks_links:
                # If there is a URL to start from, skip all until this URL is found (and skip it too)
                if self.continueFrom != '':
                    if self.continueFrom == break_link:
                        logger.logger.info(f"Continuing crawling from page {break_link}")
                        self.continueFrom = ''
                    count += 1
                    continue

                break_forecast_link = break_link + '/forecasts/latest/six_day'
                break_main_page = RequestsHandler.get(break_link)
                break_forecast_page = RequestsHandler.get(break_forecast_link)

                # If any of the pages could not be retrieved, skip it.
                if break_main_page is None or break_forecast_page is None:
                    logger.logger.warning(f"Page {break_link} could not be downloaded, skipping it...")
                    continue

                page = Break(break_main_page, break_forecast_page, break_link)
                self.output_buffer.put(page)

                count += 1
                if count == self.limit:
                    self.__close()
                    return

        self.__close()

    def __close(self):
        self.output_buffer.shutdown()

    def __get_full_url(self, host, url):
        return 'https://' + host + url['href']

    def pop(self) -> tuple[Break, bool]:
        try:
            return self.output_buffer.get(), False
        except ShutDown:
            return '', True
