import csv
import requests
import pandas as pd
import datetime
from tqdm import tqdm
from src.utils.config import settings
from dateutil.relativedelta import relativedelta
from typing import Optional
from io import StringIO

def get_last_n_months(n):
    current_date = datetime.datetime.now()
    months = []

    for i in range(n):
        month = current_date - relativedelta(months=i)
        months.append(month.strftime("%Y-%m"))

    return months

class AlphaVantage:
    def __init__(self):
        self.key = settings["ALPHAVANTAGE_KEY"]
        self.base_url = "https://www.alphavantage.co/query"
        self.params = {"apikey": self.key}

    def make_request(self, params: dict):
        params.update(self.params)
        with requests.Session() as s:
            response = s.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed retrieving {response.status_code}")
        return response

    def get_extended_intraday(
        self, ticker: str, interval: str, months: int
    ) -> pd.DataFrame:
        data = pd.DataFrame()
        if months > 24:
            raise ValueError(
                f"Invalid value for months argument: {months}. Maximum value allowed is 24."
            )
        if interval not in ["1min", "5min", "15min", "30min", "60min"]:
            raise Exception(
                'Invalid interval only following interval are available :["1min", "5min", "15min", "30min", "60min"]'
            )
        # get last 24 months in YYYY-MM format

        months = get_last_n_months(months)
        for m in months:
            with tqdm(total=len(months)) as pbar:
                pbar.set_description(f"Downloading data for {m}")
                params = {
                    "apikey": settings["ALPHAVANTAGE_KEY"],
                    "symbol": ticker,
                    "interval": interval,
                    "function": "TIME_SERIES_INTRADAY",
                    "month": m,
                    "outputsize": "full",
                }
                response = self.make_request(params=params)
                decoded_content = response.content.decode("utf-8")
                df = pd.DataFrame(response.json()[f"Time Series ({interval})"])
                df = df.transpose()
                # df = pd.DataFrame(csv.reader(decoded_content.splitlines(), delimiter=","))
                # df.columns = df.iloc[0]
                # df.drop(0, inplace=True)
                data = pd.concat([data, df])
                pbar.set_postfix(
                    rows= len(df),
                    total_rows=len(data)
                )
                pbar.update(1)
        return data

    def get_intraday(self, ticker: str, interval: str, **kwargs) -> pd.DataFrame:
        """Get Intraday data for a ticker

        Args:
            ticker (str): Ticker value
            interval (str): ["1min", "5min", "15min", "30min", "60min"]

        Returns:
            pd.DataFrame: Dataframe
        """
        # Check if the interval is valid. If not, raise a ValueError with an error message.
        if interval not in ["1min", "5min", "15min", "30min", "60min"]:
            ValueError(
                f"Invalid value for interval argument: {interval}. Only the following values are allowed: ['1min', '5min', '15min', '30min', '60min']"
            )

        # Create a dictionary containing the API parameters needed to retrieve intraday data
        params = {
            "apikey": settings["ALPHAVANTAGE_KEY"],
            "symbol": ticker,
            "interval": interval,
            "function": "TIME_SERIES_INTRADAY",
            "outputsize": "full",
            # current month
            "month" :  datetime.datetime.now().strftime("%Y-%m")
        }

        # Update the dictionary with any additional keyword arguments passed to the function
        params.update(**kwargs)

        # Send a request to the Alpha Vantage API with the updated parameters
        response = self.make_request(params=params)

        # Convert the API response to a pandas data frame and extract the intraday data
        data = pd.DataFrame(response.json()[f"Time Series ({interval})"])

        # Transpose the data frame so that the columns represent individual time points
        return data.transpose()

    def get_news_sentiment(
        self,
        tickers: str,
        from_time: datetime.datetime = datetime.datetime.now()
        - datetime.timedelta(days=7),
        to_time: datetime.datetime = datetime.datetime.now(),
        **kwargs,
    ):
        """
        **kwargs :  for additonal arguements https://www.alphavantage.co/documentation/#news-sentiment
        """
        params = {
            "function": "NEWS_SENTIMENT",
            "ticker": tickers,
            "time_from": from_time.strftime("%Y%m%dT%H%M"),
            "time_to": to_time.strftime("%Y%m%dT%H%M"),
            "limit": 1000,
        }
        response = self.make_request(params=params)
        if response.status_code != 200:
            raise Exception(f"Failed retrieving data {response.status_code}")
        
        df = pd.json_normalize(response.json()['feed'])

        return df
    
    def get_options_chain(self, ticker: str, date: datetime, **kwargs):
        """
        Get options chain for a given ticker and expiration date

        Args:
            ticker (str): Ticker symbol
            expiration_date (str): Expiration date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Options chain data
        """
        params = {
            "symbol": ticker,
            "function": "HISTORICAL_OPTIONS",
            "date" : date.strftime("%Y-%m-%d")
        }
        response = self.make_request(params=params)
        data = response.json()
        return data

    def get_us_ticker_list(self,date: Optional[datetime.datetime] = None, active: bool = True):
        # https://www.alphavantage.co/query?function=LISTING_STATUS&date=2014-07-10&state=delisted&apikey=demo
        # the API returns a CSV file
        params = {
            "function": "LISTING_STATUS",
            "date" : date.strftime("%Y-%m-%d") if date is not None else datetime.datetime.now().strftime("%Y-%m-%d"),
            "state" : "active" if active else "delisted"
        }
        response = self.make_request(params=params)
        decoded_content = response.content.decode('utf-8')
        data = pd.read_csv(StringIO(decoded_content))
        return data

if __name__ == '__main__':
    av = AlphaVantage()
    # print("Intraday")
    # data = av.get_intraday("AAPL", "5min")
    # #print(data.head())
    # print(data.shape)
    # print("Extended Intraday")
    # data = av.get_extended_intraday("AAPL", "5min", 2)
    # print(data.shape)
    # print("News Sentiment")
    # news = av.get_news_sentiment("AAPL")
    # print(news)
    print("Delisted US Ticker List")
    data = av.get_us_ticker_list(active=False)
    print(data)
