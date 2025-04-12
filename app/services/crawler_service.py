import json
import argparse
from pymongo import MongoClient
from urllib.parse import urlparse

from app.databases.mongo_services import MongoDBServices
from app.databases.crawl_url import UrlCrawler
from app.databases.crawl_item_detail import ItemDetailCrawler

class Crawler:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Crawl data')
        parser.add_argument('--crawl_type', type=str, default='item_url')
        parser.add_argument('--monggo_uri', type=str, default='mongodb://admin:251297@localhost:27017/')
        args  = parser.parse_args()
        self.crawl_type = args.crawl_type
        self.mongo_uri = args.mongo_uri

        self.url_crawler = UrlCrawler()
        self.item_detail_crawler = ItemDetailCrawler()
        self.mongo_handler = MongoDBServices(self.mongo_uri)
        self.crawl_type = args.crawl_type

    def crawling(self):
        # Read file JSON
        with open('../config/selectors_config.json', 'r') as f:
            selectors = json.load(f)
        with open('../config/monggo_db_config.json', 'r') as f:
            db_configs = json.load(f)

        if self.crawl_type == "phone_series_url":
            db_config = db_configs.get(self.crawl_type, {})
            for url, selectors_info in selectors.items():
                data, error = self.url_crawler.crawling(url, self.crawl_type, selectors_info)
                self.mongo_handler.save_to_db(data, db_config["save_db_name"], db_config["save_collection_name"])
                if len(error)>=1:
                    self.mongo_handler.save_to_db(error, db_config["save_db_name"], db_config["save_db_error"])

        elif self.crawl_type == "item_url":
            db_config = db_configs.get(self.crawl_type, {})
            series_url_data = self.mongo_handler.read_from_DB(db_config["read_db_name"], db_config["read_collection_name"])
            for url_data in series_url_data:
                series_url = url_data.get("phone_series_url")
                parsed_url = urlparse(series_url)
                web_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                selectors_info = selectors.get(web_url, {})
                data, error = self.url_crawler.crawling(series_url, self.crawl_type, selectors_info)
                self.mongo_handler.save_to_db(data, db_config["save_db_name"], db_config["save_collection_name"])
                if len(error)>=1:
                    self.mongo_handler.save_to_db(error, db_config["save_db_name"], db_config["save_db_error"])


        elif self.crawl_type == "item_detail":
            db_config = db_configs.get(self.crawl_type, {})
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



if __name__ == "__main__":
    app = Crawler()
    app.crawling()