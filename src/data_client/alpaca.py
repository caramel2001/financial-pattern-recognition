from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import OptionBarsRequest, OptionLatestQuoteRequest, OptionChainRequest
# import sys
# print(sys.path)
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
    
if __name__ == '__main__':
    api_key = settings["ALPACA_API_KEY"]
    secre_key = settings["ALPACA_SECRET_KEY"]
    print(api_key,secre_key)