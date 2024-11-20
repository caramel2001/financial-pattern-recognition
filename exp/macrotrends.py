from src.data_client.macrotrends import MacrotrendsClient
from src.database.azure_cosmos import CosmosDB
from datetime import datetime
from loguru import logger
import time
from tqdm import tqdm
client = MacrotrendsClient()

stocks = client.get_all_stocks()
# get list of tickers already present in the database
db_client = CosmosDB()
collection= db_client.get_collection(db_client.maps['macrotrends']['database'],db_client.maps['macrotrends']['collection'],db_client.maps['macrotrends']['partition_key'])
# Query to extract all IDs
query = "SELECT c.id FROM c"
items = collection.query_items(query=query, enable_cross_partition_query=True)
unique_tickers = [item['id'] for item in items]
print("Unique tickers in the database",len(unique_tickers))
no_data_stocks=['AAM/aa-mission-acquisition']
for stock in tqdm(stocks):
    if stock.replace("/","-") in unique_tickers:
        logger.info(f"Data for {stock} already present in the database")
        continue
    if stock in no_data_stocks:
        logger.info(f"No data for {stock}")
        continue
    
    try: 
        ticker = stock.split("/")[0]
        comp_name = stock.split("/")[1]
        data = client.get_all_fundamentals_data(stock)
        # store data in mongo
        mongo_data={
            "url":stock,
            "ticker":ticker,
            "comp_name":comp_name,
            "data":data,
            "updated_at":str(datetime.now())
        }
        db_client.store_macrotrends_data(mongo_data)
        logger.info(f"Data for {stock} stored in the database")
        logger.info(f"sleeping for 20 seconds")
        time.sleep(20)
    except Exception as e:
        logger.error(f"Error in extracting data for {stock}")
        logger.error(e)
        logger.info(f"Skipping {stock} and sleeping for 20 seconds")
        time.sleep(20)