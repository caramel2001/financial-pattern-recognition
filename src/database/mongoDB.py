from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from src.utils.config import settings
from loguru import logger
import pandas as pd
from tqdm import tqdm
import socket
import subprocess
import time

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
    
    def is_mongodb_running(self, host='localhost', port=27017):
        """Check if MongoDB is accepting connections on the specified port."""
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            return False
    
    def start_mongodb_service(self):
        """Start the MongoDB Windows service."""
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Start-Service -Name "MongoDB"'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("MongoDB service started.")
            else:
                logger.error("Failed to start MongoDB service:")
                logger.error(result.stderr)
        except Exception as e:
            logger.error(f"Error starting service: {e}")
    
    def check_db_connection(self):
        """Check if MongoDB is running and start it if not."""
        if self.is_mongodb_running():
            logger.info("MongoDB is already running.")
        else:
            logger.info("MongoDB is not running. Attempting to start service...")
            self.start_mongodb_service()
            # Wait and verify again
            time.sleep(3)
            if self.is_mongodb_running():
                logger.info("MongoDB started successfully.")
            else:
                logger.error("MongoDB is still not running.")
        

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
    