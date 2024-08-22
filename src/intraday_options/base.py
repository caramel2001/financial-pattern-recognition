from datetime import datetime
class BaseOptions:
    def __init__(self,ticker,start_date:datetime,end_date:datetime):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
    
    def get_historical_options(self,strike_price:int,option_type:str):
        raise NotImplementedError("This method must be implemented by the subclass.")
