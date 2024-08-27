import requests
from bs4 import BeautifulSoup
import pandas as pd
import finnhub
from src.utils.config import settings
# import StringIO
from io import StringIO

class ScreenerIn:  # for Indian stocks
    def __init__(self,ticker:str):
        self.url = f'https://www.screener.in/company/{ticker}'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36'
        }
        self.soup = self.get_page()
        self.warehouse_id = self.soup.find("div", {"id": "company-info"}).attrs['data-warehouse-id']
    
    def get_page(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to load page: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    
    def get_data(self):
        return {
            "company_info": self.get_company_info(),
            "quaterly_results": self.get_quaterly_results(),
            "peers": self.get_peers(),
            "profit_loss": self.get_profit_loss(),
            "balance_sheet": self.get_balance_sheet(),
            "cash_flow": self.get_cash_flow(),
            "ratios": self.get_ratios(),
            "shareholders": self.get_shareholders()
        }

    def get_company_info(self):
        # Extract the ratios and values
        ratios = []
        values = []
        html = self.soup.find('ul',attrs={'id':'top-ratios'})

        for li in html.find_all('li'):
            ratio_name = li.find('span', class_='name').text.strip()
            ratio_value = li.find('span', class_='number').text.strip()
            if " / " in li.find('span', class_='value').text:
                ratio_value += " / " + li.find_all('span', class_='number')[1].text.strip()
            values.append(ratio_value)
            ratios.append(ratio_name)
        df_ratios = pd.DataFrame({'Ratio': ratios, 'Value': values})
        return df_ratios

    def get_quaterly_results(self):
        html = self.soup.find('section', {'id': 'quarters'})
        table = html.find('table')
        return pd.read_html(StringIO(str(table)))[0].set_index('Unnamed: 0').transpose()
    
    def get_peers(self):
        page = requests.get(f'https://www.screener.in/api/company/{self.warehouse_id}/peers/')
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find('table')
        return pd.read_html(StringIO(str(table)))
    
    def get_profit_loss(self):
        html = self.soup.find('section', {'id': 'profit-loss'})
        table = html.find('table')
        return pd.read_html(StringIO(str(table)))[0].set_index('Unnamed: 0').transpose()
    
    def get_balance_sheet(self):
        html = self.soup.find('section', {'id': 'balance-sheet'})
        table = html.find('table')
        return pd.read_html(StringIO(str(table)))[0].set_index('Unnamed: 0').transpose()
    
    def get_cash_flow(self):
        html = self.soup.find('section', {'id': 'cash-flow'})
        table = html.find('table')
        return pd.read_html(StringIO(str(table)))[0].set_index('Unnamed: 0').transpose()
    
    def get_ratios(self):
        html = self.soup.find('section', {'id': 'ratios'})
        table = html.find('table')
        return pd.read_html(StringIO(str(table)))[0].set_index('Unnamed: 0').transpose()
    
    def get_shareholders(self):
        html = self.soup.find('section', {'id': 'shareholding'})
        table = html.find('table')
        return pd.read_html(StringIO(str(table)))[0].set_index('Unnamed: 0').transpose()


# https://www.kaggle.com/datasets/finnhub/reported-financials by FinnHubb
class FundamentalsUS: # for US stocks (Alpha Vantage)
    def __init__(self,ticker:str):
        print(settings['FINNHUB_API_KEY'])
        self.client  = finnhub.Client(api_key=settings['FINNHUB_API_KEY'])
        self.ticker = ticker    

    def get_peers(self):
        return self.client.company_peers(self.ticker)
    
    def search(self,query:str):
        return self.client.symbol_lookup(query)
    

if __name__ == "__main__":
    ticker = "MARUTI"
    screener = ScreenerIn(ticker)
    print(screener.get_data())
    # ticker = "MARUTI.NS"
    # fundamentals = FundamentalsUS(ticker)
    # print(fundamentals.get_peers())