from crawler import Crawler
from dumpDB import get_db_as_dict
from scrapper import Scrapper
import sys
import logger
from tinydb import TinyDB, Query
import plyvel
import json


def main():
    limit, output_file, log_file = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    logger.initLogger(log_file)

    db = plyvel.DB('mydb/', create_if_missing=True)

    crawler = Crawler(limit)
    scrapper = Scrapper(crawler, output_file, db)

    crawler.crawl()
    scrapper.scrap()

    db_dict = get_db_as_dict(db)

    db.close()

    with open(output_file, 'w') as f:
        json.dump(db_dict, f, indent=4)


main()
