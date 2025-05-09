from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.timeframe import TimeFrame,TimeFrameUnit
from alpaca.data.requests import OptionBarsRequest, OptionLatestQuoteRequest, StockLatestQuoteRequest,OptionChainRequest, StockBarsRequest, CryptoBarsRequest
from src.utils.config import settings
from datetime import datetime

class Options:
    def __init__(self, api_key:str,secre_key,symbol:str, start_date:datetime, end_date:datetime, timeframe:TimeFrame):
        self.api_key = api_key
        self.secre_key = secre_key
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.client = OptionHistoricalDataClient(api_key,secre_key)
    
    def get_data(self):
        request = OptionBarsRequest(symbol=self.symbol, start=self.start_date, end=self.end_date, timeframe=self.timeframe)
        data = self.client.get_option_bars(request)
        return data
    
    def get_option_chain(self,**kwargs):
        request = OptionChainRequest(symbol=self.symbol,**kwargs)
        data = self.client.get_option_chain(request)
        return data
    
class Stock:
    def __init__(self, api_key:str,secret_key, start_date:datetime=None, end_date:datetime=None, timeframe:TimeFrame = TimeFrame(1,TimeFrameUnit.Minute),raw_data:bool=False):
        self.api_key = api_key
        self.secret_key = secret_key
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.client = StockHistoricalDataClient(api_key,secret_key,raw_data=raw_data)

    def get_premarket_price(self,tickers:list):
        """Gets the latest quote for a stock"""
        request = StockLatestQuoteRequest(symbol_or_symbols=tickers)
        data = self.client.get_stock_latest_quote(request)
        return data
    
    def get_data(self,tickers:list):
        request = StockBarsRequest(symbol_or_symbols=tickers, start=self.start_date, end=self.end_date, timeframe=self.timeframe)
        data = self.client.get_stock_bars(request)
        return data

class Crypto:
    def __init__(self, api_key:str,secret_key, start_date:datetime=None, end_date:datetime=None, timeframe:TimeFrame = TimeFrame(1,TimeFrameUnit.Minute),raw_data:bool=False):
        self.api_key = api_key
        self.secret_key = secret_key
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.client = CryptoHistoricalDataClient(api_key,secret_key,raw_data=raw_data)

    def get_data(self,tickers:list):
        request = CryptoBarsRequest(symbol_or_symbols=tickers, start=self.start_date, end=self.end_date, timeframe=self.timeframe)
        data = self.client.get_crypto_bars(request)
        return data
        
if __name__ == '__main__':
    api_key = settings["ALPACA_API_KEY"]
    secret_key = settings["ALPACA_SECRET_KEY"]
    print(api_key,secret_key)