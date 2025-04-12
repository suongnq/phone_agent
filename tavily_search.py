from langchain_community.tools import TavilySearchResults
import json
import os
from urllib.parse import urlparse
from crawler.crawl_item_detail import ItemDetailCrawler
from utilis.mongo_services import MongoDBServices
from config import (
    MONGO_URI,
    PG_COLLECTION_NAME,
    PG_CONNECTION_STRING,
    MONGO_URI,
    API_KEY,
    API_MODEL,
    EMBEDDING_MODEL,
    TOP_K_SIMILAR,
    TAVILY_API_KEY,
    DOMAINS,
    MAX_RESEARCH,
)

import openai
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document

question = "Giá sản phẩm Iphone 13 Pro Max 256GB?"

info = ["{'item_url': 'https://cellphones.com.vn/iphone-13-pro-max-256gb.html', 'cats_path': 'Điện thoại|Apple|iPhone 13 Series', 'item_name': 'iPhone 13 Pro Max 256GB | Chính hãng VN/A', 'storage_capacity': '256GB', 'color': 'Vàng', 'price': '5.000.000đ', 'rating': '4.8/5', 'num_review': '33 đánh giá', '_id': ObjectId('67f6385735ef5311ab6fc0c3')}", "{'item_url': 'https://cellphones.com.vn/iphone-13-pro-max-256gb.html', 'cats_path': 'Điện thoại|Apple|iPhone 13 Series', 'item_name': 'iPhone 13 Pro Max 256GB | Chính hãng VN/A', 'storage_capacity': '256GB', 'color': 'Vàng', 'price': None, 'rating': '4.8/5', 'num_review': '33 đánh giá', '_id': ObjectId('67f6384835ef5311ab6fc0bf')}", "{'item_url': 'https://cellphones.com.vn/iphone-13-pro-max-256gb.html', 'cats_path': 'Điện thoại|Apple|iPhone 13 Series', 'item_name': 'iPhone 13 Pro Max 256GB | Chính hãng VN/A', 'storage_capacity': '256GB', 'color': 'Vàng', 'price': None, 'rating': '4.8/5', 'num_review': '33 đánh giá', '_id': ObjectId('67f6360464a530176a3b2746')}", "{'item_url': 'https://cellphones.com.vn/iphone-13-pro-max-256gb.html', 'cats_path': 'Điện thoại|Apple|iPhone 13 Series', 'item_name': 'iPhone 13 Pro Max 256GB | Chính hãng VN/A', 'storage_capacity': '256GB', 'color': 'Vàng', 'price': None, 'rating': '4.8/5', 'num_review': '33 đánh giá', '_id': ObjectId('67f636c1b12e167539cb53ca')}"]

user_prompt = f"""Câu hỏi: {question}
Thông tin tham khảo: {info}

Hãy kiểm tra xem tên sản phẩm ở câu hỏi và tên sản phẩm ở thông tin tham khảo có liên quan đến nhau không.

- Nếu rõ ràng không liên quan, chỉ trả về đúng chuỗi: "incorrect"
- Nếu có liên quan hoặc nghi ngờ có liên quan, hãy đưa ra phản hồi phù hợp dựa trên thông tin tham khảo. Không thêm lời giải thích."""

system_prompt = "Bạn là một trợ lý AI chuyên cung cấp thông tin chính xác và ngắn gọn, chỉ dựa trên dữ kiện đã có, không thêm các từ ngữ không cần thiết."
# user_prompt = f"Câu hỏi: {question}\nThông tin tham khảo: {info}\n\nHãy kiểm tra xem tên sản phẩm ở câu hỏi và tên sản phẩm ở thông tin tham khảo có liên quan đến nhau không.\n\n- Nếu không liên quan, chỉ trả về đúng chuỗi: \"incorrect\"\n- Nếu liên quan, hãy đưa ra phản hồi phù hợp dựa trên thông tin tham khảo. Không thêm lời giải thích."
response = openai.ChatCompletion.create(
        model=API_MODEL,
        messages=[
             {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            api_key=API_KEY,
            )

print(response.choices[0].message["content"].strip())
# with open("./config/selectors_config.json", "r") as f:
#     selectors = json.load(f)
#
# mongo_services=MongoDBServices(MONGO_URI)

# with open("config/monggo_db_config.json", "r") as f:
#     db_configs = json.load(f)
# db_config = db_configs.get("item_detail", {})
#
# url = "https://cellphones.com.vn/iphone-15.html"
# parsed_url = urlparse(url)
# url_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
# selector_info = selectors.get(url_domain, {})
#
# data, error = ItemDetailCrawler().crawling(url, selector_info)
#
#
#
# remove_keys = ["time"]
# # str_data = [str({k: v for k, v in doc.items() if k not in remove_keys}) for doc in data]
# docs = [
#     Document(page_content=str({k: v for k, v in doc.items() if k not in remove_keys}))
#     for doc in data
# ]
#
# print(docs)
# db = PGVector(
#     embedding_function=OpenAIEmbeddings(
#     model=EMBEDDING_MODEL, openai_api_key=API_KEY
#     ),
#     collection_name=PG_COLLECTION_NAME,
#     connection_string=PG_CONNECTION_STRING,
#     )
# db.add_documents(documents=docs)