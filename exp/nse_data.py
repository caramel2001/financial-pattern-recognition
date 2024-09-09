from src.data_client.fyers import FyersBase,FyersData
import webbrowser
from loguru import logger
from datetime import datetime,timedelta
import json

def get_auth_code():
    fyers = FyersBase()
    url = fyers.get_auth_url()
    webbrowser.open(url,new=1)

def get_access_token():
    fyers = FyersBase()
    fyers.get_access_token()
    fyers.store_token()

def get_data(tickers:list,start,end,**kwargs):
    fyers = FyersData(**kwargs)
    data = fyers.get_historical_data("SBIN-EQ","NSE",interval="1",start=start,end=end)
    print(len(data['candles']))
    print(data['candles'][0])
    print(data['candles'][-1])

def ticker_list():
    fyers = FyersData()
    fyers.get_equity_list()
    return fyers.NSE_equity_symbols, fyers.BSE_equity_symbols

def main():
    # logger.debug("Getting auth code")
    # get_auth_code()
    # logger.debug("Getting access token")
    # get_access_token()

    # NSE_tickers, _ = ticker_list()
    # NSE_tickers = NSE_tickers['symTicker'].to_list()
    # get_data()
    fyers = FyersData()
    # data = fyers.get_historical_data("SBIN-EQ","NSE",interval="1")
    
    # print(len(data['candles']))
    # print(data['candles'][0])
    # print(data['candles'][-1])
    # print(datetime.fromtimestamp(data['candles'][0][0]))
    # print(datetime.fromtimestamp(data['candles'][-1][0]))
    fyers.get_equity_list()
    intruments = fyers.NSE_equity_symbols[fyers.NSE_equity_symbols['exSeries']=="EQ"]
    tickers= intruments['symTicker'].to_list()[1585:]
    exchanges = [i.split(":")[0] for i in tickers]
    tickers = [i.split(":")[1] for i in tickers]
    main_start = datetime.now() - timedelta(days=100*10)
    main_start = main_start.replace(second=0,microsecond=0)
    
    for ticker,exchange in zip(tickers,exchanges):
        logger.debug(f"Getting data for {ticker}:{exchange}")
        data=[]
        start = datetime.now() - timedelta(days=100)
        end = datetime.now() - timedelta(minutes=1)
        for _ in range(30):
            if end < main_start:
                break
            #logger.debug("Start date: {} , End date: {}".format(start,end))
            temp = fyers.get_historical_data(ticker,exchange,start=start,end=end,interval="1")
            # logger.debug(f"Data length: {len(temp['candles'])}")
            # logger.debug(f"First candle: {datetime.fromtimestamp(temp['candles'][0][0])}")
            # logger.debug(f"Last candle: {datetime.fromtimestamp(temp['candles'][-1][0])}")
            if len(temp.get("candles",[]))==0:
                break
            end = datetime.fromtimestamp(temp['candles'][0][0]) - timedelta(days=1)
            start = end - timedelta(days=100)
            data.extend(temp['candles'])
        logger.debug(f"Data length: {len(data)}")
        with open(f"data/fyers/{ticker}_{exchange}.json","w") as f:
            json.dump(data,f)

if __name__ == "__main__":
    main()