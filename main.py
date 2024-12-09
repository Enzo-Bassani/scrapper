from crawler import Crawler
from scrapper import Scrapper
import sys
import logger


def main():
    limit, output_file, log_file = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    logger.initLogger(log_file)

    crawler = Crawler()
    scrapper = Scrapper(crawler, output_file)

    crawler.crawl()
    result = scrapper.scrap(limit)


main()
