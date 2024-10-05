import requests
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger 

def etl(response):
    #regex to find the data
    num=re.findall('(?<=div\>\"\,)[0-9\.\"\:\-\, ]*',response.text)
    text=re.findall('(?<=s\: \')\S+(?=\'\, freq)',response.text)

    #convert text to dict via json
    dicts=[json.loads('{'+i+'}') for i in num]

    #create dataframe
    df=pd.DataFrame()
    for ind,val in enumerate(text):
        df[val]=dicts[ind].values()
    df.index=dicts[ind].keys()
    # return a json

    return df.to_dict()

class MacrotrendsClient:
    def __init__(self):
        self.base_url = 'https://www.macrotrends.net'
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'})
    
    def get_financial_ratios(self, ticker):
        logger.info("Getting Financial Ratios")
        url = f'{self.base_url}/stocks/charts/{ticker}/financial-ratios?freq=Q'
        response = self.session.get(url)
        df = etl(response)
        return df
    
    def get_income_statement(self, ticker):
        logger.info("Getting Income Statement")
        url = f'{self.base_url}/stocks/charts/{ticker}/income-statement?freq=Q'
        response = self.session.get(url)
        df = etl(response)
        return df
    
    def get_balance_sheet(self, ticker):
        logger.info("Getting Balance Sheet")
        url = f'{self.base_url}/stocks/charts/{ticker}/balance-sheet?freq=Q'
        response = self.session.get(url)
        df = etl(response)
        return df
    
    def get_cash_flow(self, ticker):
        logger.info("Getting CashFlow data")
        url = f'{self.base_url}/stocks/charts/{ticker}/cash-flow-statement?freq=Q'
        response = self.session.get(url)
        df = etl(response)
        return df
    
    def get_all_fundamentals_data(self, ticker):
        logger.info(f"Getting fundamentals data for {ticker}")
        return {
            "financial_ratios": self.get_financial_ratios(ticker),
            "income_statement": self.get_income_statement(ticker),
            "balance_sheet": self.get_balance_sheet(ticker),
            "cash_flow": self.get_cash_flow(ticker)
        }
    def get_all_stocks(self):
        response = self.session.get(f"{self.base_url}/stocks/stock-screener")
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', string=re.compile(r'var originalData ='))
        script_text = script_tag.string if script_tag else ""
        pattern = r'var originalData = (.*?)];'
        match = re.search(pattern, script_text, re.DOTALL)
        if match:
            original_data_json = match.group(1)
            # Load the JSON data
            original_data = json.loads(json.dumps(original_data_json+"]"))
            data = pd.DataFrame(json.loads(original_data))
            logger.info(f"Number of Stocks: {len(data)}")
            return [f"{i}/{j}" for i,j in zip(data['ticker'],data['comp_name'])]
        else:
            logger.info("No match found for Macrotrends Stocks")
            return []                        

if __name__ == "__main__":
    client = MacrotrendsClient()
    stocks = client.get_all_stocks()

    data = client.get_all_fundamentals_data(stocks[0])
    print(data)