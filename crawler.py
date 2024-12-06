from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
import json
from requestsHandler import RequestsHandler
import threading

a_lot = 2**32
host = 'pt.surf-forecast.com'


@dataclass
class Page:
    text: str
    url: str


class Crawler:
    def __init__(self) -> None:
        self.countries_url = 'https://www.surf-forecast.com/countries'
        self.starting_URL = 'https://pt.surf-forecast.com/countries/Brazil/breaks'
        self.breaks_URLs_queue: list[str] = []

        self.breaks_buffer: list[str] = []
        self.breaks_buffer_lock = threading.Lock()
        self.breaks_buffer_consumer_semaphore = threading.Semaphore(0)

    def crawl(self):
        threading.Thread(target=self.__crawl).start()

    def __crawl(self):
        starting_page_real = BeautifulSoup(RequestsHandler.get(self.countries_url), 'html.parser')

        countries_page_links = starting_page_real.find('table').find_all('a', href=re.compile('^/countries/'))
        countries_links = [self.__get_full_url(host, link) for link in countries_page_links]

        for country_link in countries_links:
            country_page = BeautifulSoup(RequestsHandler.get(country_link), 'html.parser')

            country_page_links = country_page.find('table').find_all('a', href=re.compile('^/breaks/'))
            breaks_links = [self.__get_full_url(host, link) for link in country_page_links]

            for break_link in breaks_links:
                break_page = RequestsHandler.get(break_link)
                page = Page(break_page, break_link)
                self.__buffer_append(page)

        # Free all threads waiting for the crawler.
        self.breaks_buffer_consumer_semaphore.release(a_lot)

    def __get_full_url(self, host, url):
        return 'https://' + host + url['href']

    def __buffer_append(self, page: Page):
        with self.breaks_buffer_lock:
            self.breaks_buffer.append(page)

        # Tell consumer threads that there is content to be consumed.
        self.breaks_buffer_consumer_semaphore.release()

    def pop(self) -> tuple[Page, bool]:
        # Wait for content to be added to the buffer.
        self.breaks_buffer_consumer_semaphore.acquire()

        with self.breaks_buffer_lock:
            if len(self.breaks_buffer) == 0:
                # If the thread managed to get here and the buffer is empty,
                # the crawler has stopped producing.
                return '', True
            return self.breaks_buffer.pop(), False
