from src.data_client.fyers import FyersBase,FyersData
import webbrowser

def get_auth_code():
    fyers = FyersBase()
    url = fyers.get_auth_url()
    webbrowser.open(url,new=1)

def get_access_token():
    fyers = FyersBase()
    fyers.get_access_token()
    fyers.store_token()

def get_data(tickers:list):
    fyers = FyersData()
    data = fyers.get_historical_data("SBIN-EQ","NSE",interval="1")
    print(len(data['candles']))
    print(data['candles'][0])
    print(data['candles'][-1])

def ticker_list():
    fyers = FyersData()
    data = fyers.get_equity_list()
    return fyers.NSE_equity_symbols, fyers.BSE_equity_symbols

def main():
    get_auth_code()
    get_access_token()

    NSE_tickers, _ = ticker_list()
    NSE_tickers = NSE_tickers['symTicker'].to_list()
    get_data()