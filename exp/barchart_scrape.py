from math import log

from pyarrow import chunked_array
from src.data_client.barchart import BarchartAPI
from src.database.azure_cosmos import CosmosDB
from datetime import datetime
import asyncio
from loguru import logger


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
    await api.fetch_cookies()

    db_client = CosmosDB()

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
    

    # store expiration implied move data in cosmosDB
    db_name = db_client.maps['barchart-implied-move']['database']
    collection_name = db_client.maps['barchart-implied-move']['collection']
    partition_key = db_client.maps['barchart-implied-move']['partition_key']
    collection = db_client.get_collection(db_name, collection_name, partition_key)
    expirations['id'] = f"{symbol}-{curr_time}"
    collection.upsert_item(expirations)

    chunked_gamma_data = chunk_gamma_by_strike(gamma_exposure['data'], curr_time, symbol)
    # store gamma exposure data in cosmosDB
    logger.info("Storing data in cosmosDB")
    db_name = db_client.maps['barchart']['database']
    collection_name = db_client.maps['barchart']['collection']
    partition_key = db_client.maps['barchart']['partition_key']
    collection = db_client.get_collection(db_name, collection_name, partition_key)
    gamma_exposure['id'] = f"{symbol}-{curr_time}"
    for chunk in chunked_gamma_data:
        collection.upsert_item(chunk)

if __name__ == "__main__":
    asyncio.run(main())