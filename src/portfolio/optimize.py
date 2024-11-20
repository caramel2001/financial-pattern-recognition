from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import objective_functions,expected_returns,HRPOpt
import yfinance as yf
from datetime import date,timedelta
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from loguru import logger
import pandas as pd

class Optimizer:
    def __init__(self,tickers:list,type="HRP",start = date.today() - timedelta(days=1000),end = date.today()):
        if type not in ["HRP","EF"]:
            raise ValueError("Invalid type")
        
        self.tickers = tickers
        # download the Adj Close price one by one
        self.data = pd.DataFrame()
        for ticker in tickers:
            try:
                self.data[ticker] = yf.download(ticker, start=start, end=end)['Adj Close']
            except Exception as e:
                logger.error(f"Error downloading {ticker}: {e}")
                continue
        self.mu = mean_historical_return(self.data)
        self.S = CovarianceShrinkage(self.data).ledoit_wolf()
        self.historical_returns = expected_returns.returns_from_prices(self.data)
        self.type = type

    def get_weights(self,port_val:float):
        if self.type=="HRP":
            self.opt = HRPOpt(self.historical_returns,self.S)
            weights = self.opt.optimize()
        elif self.type=="EF":
            self.opt = EfficientFrontier(self.mu,self.S)
            self.opt.add_objective(objective_functions.L2_reg, gamma=1)
        else:
            raise ValueError("Optimizer not supported")
        
        self.opt.portfolio_performance(verbose=True)
        latest_prices = get_latest_prices(self.data)
        da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=port_val)
        
        return da.lp_portfolio()


