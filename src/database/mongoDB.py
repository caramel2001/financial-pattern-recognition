from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from src.utils.config import settings
from loguru import logger
import pandas as pd
from tqdm import tqdm

maps={
    "transcript":{
        "database":"FinancialData",
        "collection":"Transcripts"
    }
}

class MongoDB:
    def __init__(self,verbose=False):
        self.client = MongoClient(settings['MONGO_URI'], serverSelectionTimeoutMS=5000)
        if verbose:
            logger.debug("Connected to MongoDB")
            logger.debug(f"Database: {self.client.list_database_names()}")

        
    def store_transcripts(self,transcripts):
        db = self.client[maps['transcript']['database']]
        collection = db[maps['transcript']['collection']]

        for transcript in tqdm(transcripts):
            transcript['date'] = pd.to_datetime(transcript['date'])
            collection.insert_one(transcript)
