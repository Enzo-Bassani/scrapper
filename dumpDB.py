from crawler import Crawler
from scrapper import Scrapper
import sys
import logger
import plyvel
import json


def get_db_as_dict(db):
    db_dict = {}
    for key, value in db:
        db_dict[key.decode()] = json.loads(value)

    return db_dict


def main():
    output_file = sys.argv[1]
    db = plyvel.DB('mydb/', create_if_missing=False)

    db_dict = get_db_as_dict(db)

    with open(output_file, 'w') as f:
        json.dump(db_dict, f, indent=4)


if __name__ == "__main__":
    main()
