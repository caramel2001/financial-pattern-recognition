from coinbase.rest import RESTClient
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from loguru import logger
from src.utils.config import settings

class CoinbaseCrypto:
    def __init__(self, api_key, api_secret):
        self.client = RESTClient(api_key, api_secret)
        self.valid_granularity = ["ONE_MINUTE", "FIVE_MINUTE", "FIFTEEN_MINUTE", "THIRTY_MINUTE","ONE_HOUR", "TWO_HOUR","SIX_HOURS", "ONE_DAY"]
        self.granularity_multiplier = {
            "ONE_MINUTE": 60,
            "FIVE_MINUTE": 300,
            "FIFTEEN_MINUTE": 900,
            "THIRTY_MINUTE": 1800,
            "ONE_HOUR": 3600,
            "TWO_HOUR": 7200,
            "SIX_HOURS": 21600,
            "ONE_DAY": 86400
        }
   
    def get_all_products(self,**kwargs):
        return self.client.get_products(**kwargs)
    
    def get_market_data(self, product_id, granularity:str = "FIVE_MINUTE", start:datetime = datetime.now() - timedelta(days=7), end=datetime.now()):
        if granularity not in self.valid_granularity:
            raise ValueError(f"Invalid granularity. Valid values are {self.valid_granularity}")
        # convert datetime to UNIX timestamps
        start = str(int(start.timestamp()))
        end = str(int(end.timestamp()))
        data={
            "candles":[]
        }
        # iterate until all candles are fetched
        while start < end:
            curr_end = str(int(start) + self.granularity_multiplier[granularity]*350)
            if curr_end > end:
                curr_end = end
            logger.debug(f"Fetching data from {datetime.fromtimestamp(int(start))} to {datetime.fromtimestamp(int(curr_end))}")
            temp = self.client.get_candles(product_id,str(start),str(curr_end),granularity=granularity)
            data['candles'].extend(temp.get("candles",[]))
            start = curr_end
        return pd.json_normalize(data['candles']).loc[::-1]
    
    def get_minute_wise_data_kaggle(self):
        # download a public dataset from kaggle
        # https://www.kaggle.com/datasets/tencars/392-crypto-currency-pairs-at-minute-resolution
        # This dataset contains the historical trading data (OHLC) of more than 400 trading pairs at 1 minute resolution reaching back until the year 2013. It was collected from the Bitfinex exchange 
        pass

if __name__ == "__main__":
    client = CoinbaseCrypto(api_key=settings['COINBASE_API_KEY_2'], api_secret=settings['COINBASE_SECRET_KEY_2'])
    df = client.get_market_data("SOL-PERP-INTX")
    print(df)