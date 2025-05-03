from coinbase.rest import RESTClient
from binance.client import Client
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


class BinanceCrypto:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)
        self.valid_intervals = [
            "1m", "3m", "5m", "15m", "30m", 
            "1h", "2h", "4h", "6h", "12h", "1d", "3d", 
            "1w", "1M"
        ]
        self.interval_limits = {
            "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800, 
            "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "12h": 43200, 
            "1d": 86400, "3d": 259200, "1w": 604800, "1M": 2592000
        }

    def get_all_products(self):
        """Fetch all available trading pairs on Binance."""
        try:
            return self.client.get_exchange_info().get('symbols', [])
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []

    def get_market_data(self, symbol: str, interval: str = "5m", start: datetime = datetime.now() - timedelta(days=7), end: datetime = datetime.now()):
        """Fetch historical market data (candlesticks) from Binance."""
        if interval not in self.valid_intervals:
            raise ValueError(f"Invalid interval. Valid values are {self.valid_intervals}")
        
        # Convert datetime to Binance format strings
        start_str = start.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end.strftime('%Y-%m-%d %H:%M:%S')
        
        data = []

        while True:
            logger.debug(f"Fetching data from {start_str} to {end_str} for symbol {symbol}")
            try:
                temp = self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    start_str=start_str,
                    end_str=end_str,
                    limit=1000  # Binance max limit for klines
                )
                if not temp:
                    break
                data.extend(temp)
                
                # Update start time for next iteration
                last_timestamp = temp[-1][0] // 1000
                start_str = datetime.fromtimestamp(last_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                # If the last timestamp is the same as the end time, stop the loop
                if datetime.fromtimestamp(last_timestamp) >= end:
                    break

            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                break

        # Convert data to DataFrame and format columns
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume", 
            "close_time", "quote_asset_volume", "number_of_trades", 
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    
if __name__ == "__main__":
    # client = CoinbaseCrypto(api_key=settings['COINBASE_API_KEY_2'], api_secret=settings['COINBASE_SECRET_KEY_2'])
    # df = client.get_market_data("SOL-PERP-INTX")
    # print(df)

    client = BinanceCrypto(api_key=settings['BINANCE_API_KEY'], api_secret=settings['BINANCE_SECRET_KEY'])
    df = client.get_market_data("BTCUSDT", interval="1m", start=datetime.now() - timedelta(days=1))
    print(df.head())