from src.utils.config import settings
from fyers_apiv3 import fyersModel
import webbrowser
import requests
import pandas as pd
from datetime import datetime,timedelta
import calendar
import hashlib 


LOGS_DIR = "logs"


class FyersBase:
    def __init__(self) -> None:
        self.client_id = settings["FYERS_CLIENT_ID"]
        self.secret_key = settings["FYERS_SECRET"]
        self.redirect_uri = settings["FYERS_REDIRECT_URI"]
        self.state = "sample"
        self.response_type = "code"
        self.auth_code = settings["FYERS_AUTH_CODE"]
        self.session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key,
            redirect_uri=self.redirect_uri,
            response_type=self.response_type,
            state=self.state
        )
        # self.get_equity_list()
        # self.get_FO_list()

    def get_auth_url(self):
        return self.session.generate_authcode()
    
    def validate_token(self):
        # TODO: validate token
        pass

    def get_access_token(self,auth_code=None,refresh_token:bool=False):
        if refresh_token:
            url = "https://api-t1.fyers.in/api/v3/validate-refresh-token"
            headers = {
                "Content-Type":"application/json"
            }
            #print(self.client_id,self.secret_key)
            data_raw = {
                "grant_type": "refresh_token",
                # SHA-256 of api_id:app_secret. 
                "appIdHash": hashlib.sha256(f"{self.client_id}:{self.secret_key}".encode()).hexdigest(),
                "refresh_token": self.refresh_token,
                "pin": settings["FYERS_PIN"],
            }
            response = requests.post(url,headers=headers,json=data_raw)
            response = response.json()
            try:
                if response['code'] != 200:
                    raise ValueError("Unable to get access token",response)
                self.access_token = response["access_token"]
            except KeyError:
                raise ValueError("Unable to get access token",response)
            return self.access_token
        
        auth_code = auth_code or self.auth_code
        self.session.set_token(auth_code)
        self.session.grant_type = "authorization_code"
        response  = self.session.generate_token()
        try : 
            self.access_token = response["access_token"]
            self.refresh_token = response["refresh_token"]
        except KeyError:
            raise ValueError("Unable to get access token",response)
        #print(response)
        return self.access_token
    
    def store_token(self):
        "Store both access and refresh token"
        with open("token.txt","w") as f:
            f.write(self.access_token)
            f.write("\n")
            f.write(self.refresh_token)
    
    def read_token(self):
        "read both access and refresh token"
        with open("token.txt","r") as f:
            self.access_token = f.readline().strip()
            self.refresh_token = f.readline().strip()
        
        # TODO : validate token

        return self.access_token,self.refresh_token    

    def get_equity_list(self):
        columns=['lastUpdate', 'exSymbol', 'exchange','exSeries','exSymName', 'symTicker', 'exInstType', 'fyToken','segment','symDetails','exToken','exchangeName']
        response = requests.get("https://public.fyers.in/sym_details/NSE_CM_sym_master.json")
        data = pd.DataFrame.from_dict(response.json()).transpose()
        self.NSE_equity_symbols = data[columns]

        response = requests.get("https://public.fyers.in/sym_details/BSE_CM_sym_master.json")
        data = pd.DataFrame.from_dict(response.json()).transpose()
        self.BSE_equity_symbols = data[columns]

    def get_FO_list(self):
        columns=['lastUpdate', 'exSymbol', 'exchange','exSeries','exSymName', 'symTicker', 'exInstType', 'fyToken','segment','symDetails','exToken','exchangeName']
        response = requests.get("https://public.fyers.in/sym_details/NSE_FO_sym_master.json")
        data = pd.DataFrame.from_dict(response.json()).transpose()
        self.NSE_FO_symbols = data[columns]

        response = requests.get("https://public.fyers.in/sym_details/BSE_FO_sym_master.json")
        data = pd.DataFrame.from_dict(response.json()).transpose()
        self.BSE_FO_symbols = data[columns]

    def validate_exchange(self,exchange:str):
        """Possible Exchnages
        NSE (National Stock Exchange)
        MCX (Multi Commodity Exchange)
        BSE (Bombay Stock Exchange)
        """
        if exchange not in ["NSE","MCX","BSE"]:
            raise ValueError("Invalid Exchange")
        return exchange

    def validate_symbol(self,symbol:str):
        if symbol not in self.NSE_equity_symbols["exSymbol"].values:
            raise ValueError("Invalid Symbol")
        return symbol


class FyersData(FyersBase):
    def __init__(self,new_token:bool = False,refresh_token:bool=False) -> None:
        super().__init__()
        if new_token:
            self.get_access_token()
        else:
            self.read_token()
            if refresh_token:
                self.get_access_token(refresh_token=True)
        # store token 
        self.store_token()
        self.fyers = fyersModel.FyersModel(client_id=self.client_id, token=self.access_token,log_path=LOGS_DIR)
    
    def get_historical_data(self,symbol:str,exchange:str,start:datetime=None,end:datetime=None,interval:str="1D"):
        """Get historical data for a symbol
        Args:
            symbol (str): Symbol of the stock
            exchange (str): Exchange of the stock
            start (datetime): Start date
            end (datetime): End date
            interval (str): Interval of the data.["1D","D","5S","10S","15S","30S","45S","1","2","3","5","10","15","20","30","60","120","240"]
        """
        # end or  now - 1 minute
        end = end or datetime.now() - timedelta(minutes=1)
        # start or start - 100  days
        start = start or end - timedelta(days=100)
        exchange = self.validate_exchange(exchange)
        symbol = "{}:{}".format(exchange,symbol)
        interval = self.validate_interval(interval)
        # # epoch value
        # start = str(int(start.timestamp()))
        # end = str(int(end.timestamp()))
        # start = calendar.timegm(start.timetuple())
        # end = calendar.timegm(end.timetuple())
        data = {
            "symbol":symbol,
            "resolution":interval,
            "date_format":"1", 
            # yyyy-mm-dd
            "range_from": start.strftime("%Y-%m-%d"),
            "range_to": end.strftime("%Y-%m-%d"),
            "cont_flag":"1",
        }
        return self.fyers.history(data)


    def validate_interval(self,interval:str):
       """The candle resolution. Possible values are: 
        Day : 'D' or '1D'
        5 seconds : '5S'
        10 seconds : '10S'
        15 seconds : '15S'
        30 seconds : '30S'
        45 seconds : '45S'
        1 minute : '1'
        2 minute : '2'
        3 minute : '3'
        5 minute : '5'
        10 minute : '10'
        15 minute : '15'
        20 minute : '20'
        30 minute : '30'
        60 minute : '60'
        120 minute : '120'
        240 minute : '240'
        """
       if interval not in ["1D","D","5S","10S","15S","30S","45S","1","2","3","5","10","15","20","30","60","120","240"]:
              raise ValueError("Invalid Interval")
       return interval
        
    
if __name__ == "__main__":
   
    fyers = FyersBase()
    
    # generate auth code
    # url = fyers.get_auth_url()
    # webbrowser.open(url,new=1)
    
    # get access token
    # fyers.get_access_token()
    # fyers.store_token()

    # get historical data
    fyers = FyersData()
    data = fyers.get_historical_data("SBIN-EQ","NSE",interval="1")
    
    print(len(data['candles']))
    print(data['candles'][0])
    print(data['candles'][-1])
    
    


