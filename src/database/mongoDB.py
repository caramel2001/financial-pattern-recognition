from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from src.utils.config import settings
from loguru import logger
import pandas as pd
from tqdm import tqdm


class LocalMongoDB:
    def __init__(self):
        # Connect to the local MongoDB server
        self.client = MongoClient(settings['LOCAL_MONGO_URI'], serverSelectionTimeoutMS=5000)
        self.maps = {
            "barchartGamma":{
                "database": "FinancialData",
                "collection": "BarchartGamma"
            },
            "barchartImpliedMove":{
                "database": "FinancialData",
                "collection": "BarchartImpliedMove"
            }
        }
    def get_db(self, db_name):
        # Get the specified database
        return self.client[db_name]

    def get_collection(self, db_name, collection_name):
        # Get the specified collection from the database
        db = self.get_db(db_name)
        return db[collection_name]
    

class MongoDB:
    def __init__(self,verbose=False):
        self.client = MongoClient(settings['MONGO_URI'], serverSelectionTimeoutMS=5000)
        if verbose:
            logger.debug("Connected to MongoDB")
            logger.debug(f"Database: {self.client.list_database_names()}")
        self.maps ={
            "transcript":{
                "database":"FinancialData",
                "collection":"Transcripts"
            },
            "macrotrends":{
                "database":"FinancialData",
                "collection":"Macrotrends"
            }
        }
        
    def store_transcripts(self,transcripts):
        db = self.client[self.maps['transcript']['database']]
        collection = db[self.maps['transcript']['collection']]

        for transcript in tqdm(transcripts):
            transcript['date'] = pd.to_datetime(transcript['date'])
            collection.insert_one(transcript)

    def store_macrotrends_data(self,data):
        db = self.client[self.maps['macrotrends']['database']]
        collection = db[self.maps['macrotrends']['collection']]
        collection.insert_one(data)
    
    def get_macrotrends_data(self,stock_url):
        db = self.client[self.maps['macrotrends']['database']]
        collection = db[self.maps['macrotrends']['collection']]
        data = collection.find_one({"url":stock_url})
        return data
    