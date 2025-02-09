import requests
import pandas as pd
from loguru import logger

class SeekingAlpha:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
 
    def get_data_tickers(self,tickers:str):
        metrics = self.get_metrics_tickers(tickers)
        grades = self.get_tickers_grades(tickers)
        ticker_data = []
        for i in metrics['included']:
            if i['type'] == 'ticker':
                ticker_data.append(i)
        screen_df = pd.json_normalize(ticker_data)
        screen_df.set_index('id',inplace=True)

        screen_df = self.join_metrics_grades(screen_df,metrics,grades)
        return screen_df

    def get_screen_stocks(self):
        url = "https://seekingalpha.com/api/v3/screener_results"
        params = {"filter":{"quant_rating":{"gte":3.5,"lte":5,"exclude":False},"sell_side_rating":{"gte":3.5,"lte":5,"exclude":False},"value_category":{"gte":1,"lte":6,"exclude":False},"growth_category":{"gte":1,"lte":6,"exclude":False},"profitability_category":{"gte":1,"lte":6,"exclude":False},"momentum_category":{"gte":1,"lte":6,"exclude":False},"eps_revisions_category":{"gte":1,"lte":6,"exclude":False},"authors_rating":{"gte":3.5,"lte":5,"exclude":False}},"page":1,"per_page":100,"sort":None,"total_count":True,"type":"stock"}

        response = requests.post(url, json=params,headers={'Content-Type': 'application/json','User-Agent':'Mozilla/5.0'})
        screen_stocks = response.json()
        logger.debug("Seeking Alpha Screen response status code: " + str(response.status_code))
        logger.debug("Seeking Alpha Screen response: " + str(screen_stocks))
        screen_df = pd.json_normalize(screen_stocks['data'])
        screen_df.set_index('id',inplace=True)

        metrics = self.get_metrics(screen_stocks)
        grades = self.get_grades(screen_stocks)

        screen_df = self.join_metrics_grades(screen_df,metrics,grades)

        return screen_df
    
    def get_metrics_tickers(self,tickers:str):
        """Tickers is a comma separated string of tickers"""
        url = "https://seekingalpha.com/api/v3/metrics"
        params={
            "filter[fields]":"quant_rating,authors_rating,sell_side_rating,marketcap_display,dividend_yield",
            "filter[slugs]":tickers,
            "minified":"false"
        }

        response = requests.get(url, params=params,headers={'Content-Type': 'application/json','User-Agent':'Mozilla/5.0'})
        metrics = response.json()
        return metrics

    def get_metrics(self,screen_stocks):
        metrics = self.get_metrics_tickers(",".join([i['attributes']['slug']  for i in screen_stocks['data']]))
        return metrics
    
    def get_tickers_grades(self,tickers:str):
        url = "https://seekingalpha.com/api/v3/ticker_metric_grades"
        params={
            "filter[fields]":"value_category,growth_category,profitability_category,momentum_category,eps_revisions_category",
            "filter[slugs]":tickers,
            "filter[algos][]":["etf","dividends","main_quant","reit","reit_dividend"],
            "minified":"false"
        }
        response = requests.get(url, params=params,headers={'Content-Type': 'application/json','User-Agent':'Mozilla/5.0'})
        grades = response.json()
        return grades
    
    def get_grades(self,screen_stocks):
        grades = self.get_tickers_grades(",".join([i['attributes']['slug']  for i in screen_stocks['data']]))
        return grades
    
    def join_metrics_grades(self,screen_df,metrics,grades):
        # additional ticker data
        ticker_data=[]
        for i in metrics['included']: # fill each metric 
            if i['type'] == "ticker":   
                ticker_data.append((i['id'],i['attributes']['tradingViewSlug'],i['attributes']['exchange'],i['attributes']['followersCount']))
        ticker_df = pd.DataFrame(ticker_data,columns=['id','tradingViewSlug','exchange','followersCount'])
        screen_df = screen_df.join(ticker_df.set_index('id'))

        metric_dict={}
        for i in metrics['included']:
            if i['type'] == 'metric_type':
                metric_dict[i['id']] = i['attributes']['field']
        for i in metric_dict: # creating empty columns for each metric
            screen_df[metric_dict[i]] = None
        for i in metrics['data']: # fill each metric 
            metric_name = metric_dict[i['relationships']['metric_type']['data']['id']]
            ticker = i['relationships']['ticker']['data']['id']
            value = i['attributes']['value']
            screen_df.loc[ticker,metric_name] = value

        metric_dict={}
        for i in grades['included']:
            if i['type'] == 'metric_type':
                metric_dict[i['id']] = i['attributes']['field']
        for i in metric_dict: # creating empty columns for each metric
            screen_df[metric_dict[i]] = None
        for i in grades['data']: # fill each metric 
            metric_name = metric_dict[i['relationships']['metric_type']['data']['id']]
            ticker = i['relationships']['ticker']['data']['id']
            value = (i['attributes']['grade'])
            screen_df.loc[ticker,metric_name] = value
        return screen_df
    
if __name__=="__main__":
    sa = SeekingAlpha()
    screen_df = sa.get_screen_stocks()
    print(screen_df)
    screen_df.to_csv("data/seeking_alpha_screen.csv")

    tickers = "AAPL,MSFT,GOOGL"
    df = sa.get_data_tickers(tickers)
    print(df)
    df.to_csv("data/seeking_alpha_tickers.csv")
    
