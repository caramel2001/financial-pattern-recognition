import requests
from bs4 import BeautifulSoup
import pandas as pd

class ScreenerIn:
    def __init__(self,ticker:str):
        self.url = f'https://www.screener.in/company/{ticker}'
        self.headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        self.soup = self.get_page()
    
    def get_page(self):
        response = requests.get(self.url+"/consolidated/", headers=self.headers)
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
        html = self.soup.find('table', {'id': 'quarters'})
        table = html.find('table')
        return pd.read_html(str(table))[0].set_index('Unnamed: 0').transpose()
    
    def get_peers(self):
        html = self.soup.find('table', {'id': 'peers'})
        table = html.find('table')
        return pd.read_html(str(table))[0].set_index('Unnamed: 0').transpose()
    
    def get_profit_loss(self):
        html = self.soup.find('table', {'id': 'profit-loss'})
        table = html.find('table')
        return pd.read_html(str(table))[0].set_index('Unnamed: 0').transpose()
    
    def get_balance_sheet(self):
        html = self.soup.find('table', {'id': 'balance-sheet'})
        table = html.find('table')
        return pd.read_html(str(table))[0].set_index('Unnamed: 0').transpose()  
    
    def get_cash_flow(self):
        html = self.soup.find('table', {'id': 'cash-flow'})
        table = html.find('table')
        return pd.read_html(str(table))[0].set_index('Unnamed: 0').transpose()
    
    def get_ratios(self):
        html = self.soup.find('table', {'id': 'ratios'})
        table = html.find('table')
        return pd.read_html(str(table))[0].set_index('Unnamed: 0').transpose()
    
    def get_shareholders(self):
        html = self.soup.find('table', {'id': 'shareholding'})
        table = html.find('table')
        return pd.read_html(str(table))[0].set_index('Unnamed: 0').transpose()

    