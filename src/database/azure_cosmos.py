from azure.cosmos import CosmosClient, PartitionKey, exceptions
from src.utils.config import settings
from loguru import logger
import pandas as pd
from tqdm import tqdm
import uuid

class CosmosDB:
    def __init__(self, verbose=False):
        # Initialize the Cosmos DB client
        self.client = CosmosClient(settings['COSMOS_URI'],  {'masterKey': settings['COSMOS_KEY']})
        if verbose:
            logger.debug("Connected to CosmosDB")
            logger.debug(f"Databases: {self.client.list_databases()}")
        self.maps = {
            "transcript": {
                "database": "FinancialData",
                "collection": "Transcripts",
                "partition_key": "/date"  # Define a partition key for Cosmos DB collections
            },
            "macrotrends": {
                "database": "FinancialData",
                "collection": "Macrotrends",
                "partition_key": "/updated_at"  # Define a partition key for Cosmos DB collections
            },
            "barchart": {
                "database": "FinancialData",
                "collection": "barchart",
                "partition_key": "/id"  # Define a partition key for Cosmos DB collections
            },
            "barchart-implied-move": {
                "database": "FinancialData",
                "collection": "barchart-implied-move",
                "partition_key": "/id"  # Define a partition key for Cosmos DB collections
            }
        }

    def get_database(self, db_name):
        try:
            return self.client.get_database_client(db_name)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def get_collection(self, db_name, collection_name, partition_key):
        db = self.get_database(db_name)
        try:
            return db.get_container_client(collection_name)
        except exceptions.CosmosResourceNotFoundError:
            return db.create_container(id=collection_name, partition_key=PartitionKey(path=partition_key))

    def store_transcripts(self, transcripts):
        db_name = self.maps['transcript']['database']
        collection_name = self.maps['transcript']['collection']
        partition_key = self.maps['transcript']['partition_key']
        collection = self.get_collection(db_name, collection_name, partition_key)

        for transcript in tqdm(transcripts):
            transcript['date'] = str(pd.to_datetime(transcript['date']).isoformat())  # Ensure the date is stored as ISO format
            if 'id' not in transcript:
                transcript['id'] = str(uuid.uuid4())  # Generate a unique UUID
            collection.upsert_item(transcript)

    def store_macrotrends_data(self, data):
        db_name = self.maps['macrotrends']['database']
        collection_name = self.maps['macrotrends']['collection']
        partition_key = self.maps['macrotrends']['partition_key']
        collection = self.get_collection(db_name, collection_name, partition_key)

        data['date'] = pd.to_datetime(data['updated_at']).isoformat()  # Ensure the date is stored as ISO format
        if 'id' not in data:
            data['id'] = data['url'].replace("/","-")  # Use the URL as the unique identifier
        collection.upsert_item(data)
        

