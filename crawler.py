from bs4 import BeautifulSoup
import re
import json
from requestsHandler import RequestsHandler
import threading


class Crawler:
    def __init__(self) -> None:
        self.starting_URL = 'https://pt.surf-forecast.com/countries/Brazil/breaks'
        self.breaks_URLs_queue: list[str] = []

        self.breaks_buffer: list[str] = []
        self.breaks_buffer_lock = threading.Lock()
        self.breaks_buffer_consumer_semaphore = threading.Semaphore(0)

    def crawl(self):
        threading.Thread(target=self.__crawl).start()

    def __crawl(self):
        # URL of the webpage you want to download
        url = "https://pt.surf-forecast.com/countries/Brazil/breaks"

        # Step 1: Download the webpage content
        starting_page = BeautifulSoup(RequestsHandler.get(url), 'html.parser')

        table = starting_page.find('table')
        links = table.find_all('a', href=True)
        breaks_links = ['https://pt.surf-forecast.com' + link['href'] for link in links if link['href'].startswith('/breaks/')]

        for break_link in breaks_links:
            break_page = RequestsHandler.get(break_link)
            self.__buffer_append(break_page)

    def __buffer_append(self, page: str):
        with self.breaks_buffer_lock:
            self.breaks_buffer.append(page)

        # Tell consumer threads that there is content to be consumed.
        self.breaks_buffer_consumer_semaphore.release()

    def pop(self) -> str:
        # Wait for content to be added to the buffer.
        self.breaks_buffer_consumer_semaphore.acquire()

        with self.breaks_buffer_lock:
            return self.breaks_buffer.pop()
