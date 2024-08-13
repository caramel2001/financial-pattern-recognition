import pandas as pd
import yfinance as yf

class OneMinuteData:
    """Data Class to extract one minute data from Yahoo Finance API"""
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
    
    def get_data(self):
        """Extract one minute data from Yahoo Finance API"""
        data = yf.download(self.ticker, start=self.start_date, end=self.end_date, interval='1m')
        self.data = data
        return data
    
    def store_data(self, filename):
        """Store the data in a CSV file"""
        self.data.to_csv(filename)
    
