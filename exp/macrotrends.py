from src.data_client.macrotrends import MacrotrendsClient
from src.database.mongoDB import MongoDB
from src.utils.config import settings
from datetime import datetime
from loguru import logger
import time
client = MacrotrendsClient()

stocks = client.get_all_stocks()
# get list of tickers already present in the database
mongo_client = MongoDB()
db = mongo_client.client[mongo_client.maps['macrotrends']['database']]
collection = db[mongo_client.maps['macrotrends']['collection']]
unique_tickers = collection.distinct("url")

no_data_stocks=['AAM/aa-mission-acquisition']
for stock in stocks[20:]:
    if stock in unique_tickers:
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
            "updated_at":datetime.now()
        }
        mongo_client.store_macrotrends_data(mongo_data)
        logger.info(f"Data for {stock} stored in the database")
    except Exception as e:
        logger.error(f"Error in extracting data for {stock}")
        logger.error(e)
        break
        # logger.info(f"Skipping {stock} and sleeping for 20 seconds")
        # time.sleep(20)