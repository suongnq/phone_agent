from pymongo import MongoClient

class MongoDBServices:
    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri

    def read_from_db(self, db_name, collection_name):
        client = MongoClient(self.mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        documents = collection.find()
        return documents

    def save_to_db(self, data, db_name, collection_name):
        # print("------ Save to MongoDB")
        try:
            client = MongoClient(self.mongo_uri)
            db = client[db_name]
            collection = db[collection_name]
            collection.insert_many(data)
            # print("------ Finish save")

        except Exception as e:
            # print(f"error: {e}")
            pass

