import os
from dotenv import load_dotenv

load_dotenv()

PG_COLLECTION_NAME = os.getenv("PG_COLLECTION_NAME")
PG_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING")

MONGO_URI = os.getenv("MONGO_URI")

API_KEY = os.getenv("API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

EMBEDDING_MODEL = "text-embedding-3-small"
API_MODEL = "gpt-4o-mini"
TOP_K_SIMILAR = 4
MAX_RESEARCH = 4
DOMAINS = [
    "https://bachlongmobile.com",
    "https://cellphones.com.vn",
    "https://hoanghamobile.com",
    "https://dienmaycholon.com",
]

PATH_CRAWLER_SELECTORS = "app/utils/crawler_selectors.json"
PATH_DB_NAME_CONFIGS = "app/utils/db_name_configs.json"
PATH_SYSTEM_PROMPTS = "app/utils/system_prompts.json"

CRAWL_PHONE_SERIES_URL_TYPE = "phone_series_url"
CRAWL_ITEM_URL_TYPE = "item_url"
CRAWL_ITEM_DETAIL_TYPE = "item_detail"
