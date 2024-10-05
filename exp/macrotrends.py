from src.data_client.macrotrends import MacrotrendsClient
from src.database.mongoDB import MongoDB
from src.utils.config import settings
from datetime import datetime
from loguru import logger
client = MacrotrendsClient()

stocks = client.get_all_stocks()
# get list of tickers already present in the database
mongo_client = MongoDB()
db = mongo_client.client[mongo_client.maps['macrotrends']['database']]
collection = db[mongo_client.maps['macrotrends']['collection']]
unique_tickers = collection.distinct("url")


for stock in stocks:
    if stock in unique_tickers:
        logger.info(f"Data for {stock} already present in the database")
        continue
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