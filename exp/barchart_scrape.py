import sys
import os
# get current file path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_client.barchart import BarchartAPI
from src.database.azure_cosmos import CosmosDB
from src.database.mongoDB import LocalMongoDB
from datetime import datetime
import asyncio
from loguru import logger
log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "barchart.log")
logger.add(log_file, rotation="10 MB", encoding="utf8")

def chunk_gamma_by_strike(gamma_data, datetime,symbol="$SPX"):
    """
    Splits large gamma exposure data into chunks by strikePrice and adds a timestamp.
    Each chunk will be stored as an independent document in CosmosDB.
    """

    chunks = []
    for strike, entries in gamma_data.items():
        chunks.append({
            "id" : f"{symbol}-{strike}-{datetime}",
            "symbol": symbol,
            "strikePrice": strike,
            "datetime": datetime,
            "data": entries
        })

    return chunks

async def main():
    symbol = "$SPX"
    logger.info(f"Scraping data for {symbol}")
    api = BarchartAPI()
    logger.info("Fetching cookies")
    # await api.fetch_cookies()
    api.request_cookies()

    db_client = LocalMongoDB()

    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Fetching data from Barchart at {curr_time}")
    # get expirations data
    logger.info("Fetching expirations data")
    expirations = api.get_option_expirations(symbol)
    # get in play dates
    logger.info("Fetching in play dates")
    in_play_expiry_dates = api.get_in_play_dates(expirations)
    # get gamma exposure data
    logger.info("Fetching gamma exposure data")
    gamma_exposure = api.get_gamma_exposure(symbol, in_play_expiry_dates)
    # add current time to gamma exposure data and expirations
    gamma_exposure['datetime'] = curr_time
    expirations['datetime'] = curr_time
    
    # check mongoDB connection
    db_client.check_db_connection()

    # store expiration implied move data in mongoDB
    db_name = db_client.maps['barchartImpliedMove']['database']
    collection_name = db_client.maps['barchartImpliedMove']['collection']
    collection = db_client.get_collection(db_name, collection_name)
    expirations['id'] = f"{symbol}-{curr_time}"
    expirations['datetime'] = curr_time
    expirations['symbol'] = symbol
    collection.insert_one(expirations)

    chunked_gamma_data = chunk_gamma_by_strike(gamma_exposure['data'], curr_time, symbol)
    # store gamma exposure data in mongoDB
    logger.info("Storing data in mongoDB")
    db_name = db_client.maps['barchartGamma']['database']
    collection_name = db_client.maps['barchartGamma']['collection']
    collection = db_client.get_collection(db_name, collection_name)
    gamma_exposure['datetime'] = curr_time
    gamma_exposure['symbol'] = symbol
    gamma_exposure['id'] = f"{symbol}-{curr_time}"
    for chunk in chunked_gamma_data:
        collection.insert_one(chunk)

if __name__ == "__main__":
    asyncio.run(main())