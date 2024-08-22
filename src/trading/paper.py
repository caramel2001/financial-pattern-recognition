from alpaca.trading.client import TradingClient

class PaperFolio:
    def __init__(self,api_key:str,secre_key:str):
        self.api_key = api_key
        self.secre_key = secre_key
        self.client = TradingClient(api_key,secre_key,paper=True)

    