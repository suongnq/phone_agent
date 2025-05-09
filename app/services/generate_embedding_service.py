import tiktoken
from langchain_core.documents import Document
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import OpenAIEmbeddings

from app.databases.mongo import MongoDBServices
from app.configs import MONGO_URI, EMBEDDING_MODEL, API_KEY, PG_COLLECTION_NAME, PG_CONNECTION_STRING

def execute_generate_embedding():
    try:
        # Get library
        mongo_db = MongoDBServices(MONGO_URI)

        # Get dataset
        item_detail_cursor = mongo_db.read_from_db("data", "item_detail")
        item_detail_data = list(item_detail_cursor)

        # Get data to create embedding
        remove_keys = ["time"]
        item_detail_str_data = [
            str({k: v for k, v in doc.items() if k not in remove_keys})
            for doc in item_detail_data[:5]
        ]
        documents = [Document(page_content=text) for text in item_detail_str_data]
        print(len(item_detail_str_data))

        #Create embedding
        db = PGVector.from_documents(
            embedding=OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=API_KEY),
            documents=documents,
            collection_name=PG_COLLECTION_NAME,
            connection_string=PG_CONNECTION_STRING,
        )
        return True

    except Exception:
        return False
