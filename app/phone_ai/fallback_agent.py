import argparse
from urllib.parse import urlparse
from langchain.schema import Document
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import OpenAIEmbeddings

# import warnings
# warnings.simplefilter("ignore")

class FallbackAgent:
    def __init__(
        self,
        api_key,
        embedding_model,
        pg_collection_name,
        pg_connection_string,
        ItemDetailCrawler,
        MongoDBServices,
        db_configs,
        all_selectors,
    ):
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.pg_collection_name = pg_collection_name
        self.pg_connection_string = pg_connection_string
        self.item_detail_crawler = ItemDetailCrawler
        self.mongo_services = MongoDBServices
        self.db_configs = db_configs
        self.all_selectors = all_selectors

    def embedding_generator(self, data):
        remove_keys = ["time"]
        docs = [
            Document(page_content=str({k: v for k, v in doc.items() if k not in remove_keys}))
            for doc in data
        ]
        db = PGVector(
            embedding_function=OpenAIEmbeddings(
                model=self.embedding_model, openai_api_key=self.api_key
            ),
            collection_name=self.pg_collection_name,
            connection_string=self.pg_connection_string,
        )
        db.add_documents(documents=docs)

    def crawling(self, url):
        success_count = 0
        parsed_url = urlparse(url)
        url_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        selector_info = self.all_selectors.get(url_domain, {})
        data, error = self.item_detail_crawler.crawling(url, selector_info)
        db_config = self.db_configs.get("item_detail", {})
        return data, error, db_config

    def crawl_embed_store_agent(self, state):
        search_urls = state.get("search_urls_output", "")
        success_count = 0
        print("-------- Please wait, crawling data...---------")
        for url in search_urls:
            try:
                # print(f"Crawling: {url}")
                print(url)
                data, error, db_config = self.crawling(url)
                if len(data) >= 1:
                    self.mongo_services.save_to_db(
                        data,
                        db_config["save_db_name"],
                        db_config["save_collection_name"],
                    )
                    self.embedding_generator(data)
                    success_count += 1
                else:
                    self.mongo_services.save_to_db(
                        error, db_config["save_db_name"], db_config["save_db_error"]
                    )

            except Exception:
                pass

        return {"success_count_output": success_count}