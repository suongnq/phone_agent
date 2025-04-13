import json
import argparse
from pymongo import MongoClient
from urllib.parse import urlparse

from app.databases.mongo import MongoDBServices
from app.crawler.crawl_url import UrlCrawler
from app.crawler.crawl_item_detail import ItemDetailCrawler
from app.configs import (
    MONGO_URI,
    PATH_CRAWLER_SELECTORS,
    PATH_DB_NAME_CONFIGS,
    PATH_SYSTEM_PROMPTS,
    CRAWL_PHONE_SERIES_URL_TYPE,
    CRAWL_ITEM_URL_TYPE,
    CRAWL_ITEM_DETAIL_TYPE
)

class Crawler:
    def __init__(self):
        self.mongo_uri = MONGO_URI

        self.url_crawler = UrlCrawler()
        self.item_detail_crawler = ItemDetailCrawler()
        self.mongo_handler = MongoDBServices(self.mongo_uri)

    def crawling(self, crawl_type):
        try:
            # Read file JSON
            with open(PATH_CRAWLER_SELECTORS, 'r') as f:
                selectors = json.load(f)
            with open(PATH_DB_NAME_CONFIGS, 'r') as f:
                db_configs = json.load(f)

            if crawl_type == CRAWL_PHONE_SERIES_URL_TYPE:
                db_config = db_configs.get(crawl_type, {})
                for url, selectors_info in selectors.items():
                    data, error = self.url_crawler.crawling(url, crawl_type, selectors_info)
                    self.mongo_handler.save_to_db(data, db_config["save_db_name"], db_config["save_collection_name"])
                    if len(error)>=1:
                        self.mongo_handler.save_to_db(error, db_config["save_db_name"], db_config["save_db_error"])

            elif crawl_type == CRAWL_ITEM_URL_TYPE:
                db_config = db_configs.get(crawl_type, {})
                series_url_data = self.mongo_handler.read_from_DB(db_config["read_db_name"], db_config["read_collection_name"])
                for url_data in series_url_data:
                    series_url = url_data.get("phone_series_url")
                    parsed_url = urlparse(series_url)
                    web_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    selectors_info = selectors.get(web_url, {})
                    data, error = self.url_crawler.crawling(series_url, crawl_type, selectors_info)
                    self.mongo_handler.save_to_db(data, db_config["save_db_name"], db_config["save_collection_name"])
                    if len(error)>=1:
                        self.mongo_handler.save_to_db(error, db_config["save_db_name"], db_config["save_db_error"])


            elif crawl_type == CRAWL_ITEM_DETAIL_TYPE:
                db_config = db_configs.get(crawl_type, {})
                item_url_data = self.mongo_handler.read_from_db(db_config["read_db_name"], db_config["read_collection_name"])
                for url_data in item_url_data:
                    item_url = url_data.get("item_url")
                    parsed_url = urlparse(item_url)
                    web_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    selectors_info = selectors.get(web_url, {})
                    data, error = self.item_detail_crawler.crawling(item_url, selectors_info)
                    self.mongo_handler.save_to_db(data, db_config["save_db_name"], db_config["save_collection_name"])
                    if len(error)>=1:
                        self.mongo_handler.save_to_db(error, db_config["save_db_name"], db_config["save_db_error"])
            else:
                print("Not exist crawl type")
            print("---------------------- Finish.")

            return True

        except Exception:
            return False



# if __name__ == "__main__":
#     app = Crawler()
#     crawl_type = "item_detail"
#     app.crawling(crawl_type)