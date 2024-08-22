from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest
from datetime import datetime
from src.utils.config import settings
import pandas as pd
class AlpacaNews:
    """Alpaca News"""
    def __init__(self,api_key:str,secret_key:str):
        self.client = NewsClient(api_key=api_key,secret_key=secret_key,raw_data=True)
    
    def get_news(self,symbols:str=None,start:datetime=None,include_content:bool=False):
        request_params = NewsRequest(
                        symbols=symbols,
                        start=start,
                        include_content=include_content,
                        limit=50
                        )
        news = self.client.get_news(request_params)

        return pd.json_normalize(news['news'])
    
if __name__ == '__main__':
    news = AlpacaNews(api_key=settings["ALPACA_API_KEY"],secret_key=settings["ALPACA_SECRET_KEY"])
    news_df = news.get_news("TSLA",datetime.strptime("2024-07-01", '%Y-%m-%d'))
    print(news_df)
    news_df.to_csv("news.csv",index=False)