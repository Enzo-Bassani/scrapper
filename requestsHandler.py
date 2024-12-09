import requests
import time
import threading
import os
import logger

initialTime = time.time()


class RequestsHandler:
    rate_limit_seconds = 8
    last_request_time = 0.0
    lock = threading.Lock()

    @staticmethod
    def __wait_for_rate_limit():
        """Wait until we can make a request based on rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - RequestsHandler.last_request_time
        if time_since_last_request < RequestsHandler.rate_limit_seconds:
            time_to_wait = RequestsHandler.rate_limit_seconds - time_since_last_request
            time.sleep(time_to_wait)

    @staticmethod
    def __get_cache_key(url: str) -> str:
        return url + '.file'

    @staticmethod
    def __get_cached(url: str):
        url = RequestsHandler.__get_cache_key(url)
        if os.path.exists(url):
            with open(url, 'r') as file:
                return file.read()
        return None

    @staticmethod
    def __update_cache(url: str, value):
        url = RequestsHandler.__get_cache_key(url)

        dir_name, file_name = os.path.split(url)

        os.makedirs(dir_name, exist_ok=True)
        with open(url, 'w') as file:
            return file.write(value)

    @staticmethod
    def get(url: str):
        """
        Make an HTTP request.
        """

        cached = RequestsHandler.__get_cached(url)
        if cached is not None:
            return cached

        with RequestsHandler.lock:  # Ensure only one thread can make a request at a time
            RequestsHandler.__wait_for_rate_limit()  # Ensure rate limit is respected
            logger.logger.info(f"Getting url {url}\nTime: {time.time() - initialTime}")
            response = requests.get(url)

            # Update the time of the last request after the request is made
            RequestsHandler.last_request_time = time.time()

            result = response.text

            RequestsHandler.__update_cache(url, result)

            return result
