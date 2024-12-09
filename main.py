from crawler import Crawler
from dumpDB import get_db_as_dict
from scrapper import Scrapper
import sys
import logger
import plyvel
import json
from queue import Queue


def main():
    limit, output_file, log_file = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    logger.initLogger(log_file)

    db = plyvel.DB('db/', create_if_missing=True)
    config = plyvel.DB('config', create_if_missing=True)
    config_is_initialized = config.get((b'finished'))
    if not config_is_initialized:
        config.put(b'lastScrappedURL', b'')
        config.put(b'finished', b'T')

    pages_queue = Queue()
    crawler = Crawler(pages_queue, limit, config)
    scrapper = Scrapper(pages_queue, output_file, db, config)

    crawler.crawl()
    scrapper.scrap()

    db_dict = get_db_as_dict(db)

    db.close()

    with open(output_file, 'w') as f:
        json.dump(db_dict, f, indent=4)


main()
