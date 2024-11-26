# Make an agent using LLM to decide whether to buy or sell a crypto isolated perpetual future. The LLM can access data such as orderbook and orderbook feature, tehcnical indicators and news.
import openai
from src.utils.config import settings
from src.feature.orderbook import CryptoOrderbook
from src.data_client.crypto import CoinbaseCrypto
import talib as ta
from datetime import datetime,timedelta
import pandas as pd
import mplfinance as mpf
from ccxt.coinbaseadvanced import coinbaseadvanced

class TradingAgent:
    def __init__(self,symbol="SOL/USDT"):
        self.openai = openai.OpenAI(api_key=settings["OPENAI_API_KEY"])

        self.symbol = symbol
        self.crypto_client = CoinbaseCrypto(api_key=settings['COINBASE_API_KEY_2'], api_secret=settings['COINBASE_SECRET_KEY_2'])

    def get_orderbook_data(self,price_level_increment=0.5):
        client = CryptoOrderbook()
        # Define necessary parameters
        symbol = self.symbol
        depth = 10000
        param = {
            "limit": depth,
            "symbol": symbol,
        }
        exchange = coinbaseadvanced({
            'defaultType' : "swap",
        })
        orderbooks = client._fetch_orderbook(symbol=symbol, exchange=exchange,fetch_ob_params=param)
        # Process the order books
        pd_aggregated_orderbooks_asks, pd_aggregated_orderbooks_bids,orderbook_features = client.post_process_orderbook([orderbooks], price_level_increment=price_level_increment)

        # get plot 
        return pd_aggregated_orderbooks_asks, pd_aggregated_orderbooks_bids,orderbook_features

    def get_market_data(self):
        """This function will extract the market data from CoinbaseCrypto, calculate the technical indicators and return the features. It extracts data for two time frames: 15 min intervals for the last 3 days and 1 day intervals for the last 30 days. All the indicators are calculated on the 15 min intervals.
        The function returns a dictionary with the following keys:
        'fifteen_min_interval': The market data for the last 3 days for 15 min intervals.
        'one_day_interval': The market data for the last 30 days for 1 day intervals.
        'features': A dictionary of the technical indicators calculated on the 15 min intervals.
        """
        client = CoinbaseCrypto(api_key=settings['COINBASE_API_KEY_2'], api_secret=settings['COINBASE_SECRET_KEY_2'])
        # get market data for last 3 days of 15 min intervals
        fifteen_min_interval = client.get_market_data(self.symbol,granularity="FIFTEEN_MINUTE",start=datetime.now() - timedelta(days=3))
        # convert start to datetime
        fifteen_min_interval['start'] = pd.to_datetime(fifteen_min_interval['start'], unit='s')
        # rename start to timestamp
        fifteen_min_interval.rename(columns={'start': 'timestamp'}, inplace=True)
        # convert low,open,close,high,volume to float
        fifteen_min_interval['low'] = fifteen_min_interval['low'].astype(float)
        fifteen_min_interval['open'] = fifteen_min_interval['open'].astype(float)
        fifteen_min_interval['close'] = fifteen_min_interval['close'].astype(float)
        fifteen_min_interval['high'] = fifteen_min_interval['high'].astype(float)
        fifteen_min_interval['volume'] = fifteen_min_interval['volume'].astype(float)

        # get the chart
        fifteen_min_interval_chart = self.plot_market_data(fifteen_min_interval.set_index("timestamp"),title="Candlestick Chart with Volume for 15 Min Intervals",mav=(20,50))

        # get market data for last 30 days for 1 day intervals
        one_day_interval = client.get_market_data(self.symbol,granularity="ONE_DAY",start=datetime.now() - timedelta(days=30))
        # convert start to datetime
        one_day_interval['start'] = pd.to_datetime(one_day_interval['start'], unit='s')
        # rename start to timestamp
        one_day_interval.rename(columns={'start': 'timestamp'}, inplace=True)
        # convert low,open,close,high,volume to float
        one_day_interval['low'] = one_day_interval['low'].astype(float)
        one_day_interval['open'] = one_day_interval['open'].astype(float)
        one_day_interval['close'] = one_day_interval['close'].astype(float)
        one_day_interval['high'] = one_day_interval['high'].astype(float)
        one_day_interval['volume'] = one_day_interval['volume'].astype(float)

        # get technical indicators
        # MACD
        macd = ta.MACD(fifteen_min_interval['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        # RSI
        rsi = ta.RSI(fifteen_min_interval['close'], timeperiod=14)
        # Bollinger Bands
        upper_band, middle_band, lower_band = ta.BBANDS(fifteen_min_interval['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        # SMA
        sma = ta.SMA(fifteen_min_interval['close'], timeperiod=20)

        # get volatility feature
        atr = ta.ATR(fifteen_min_interval['high'], fifteen_min_interval['low'], fifteen_min_interval['close'], timeperiod=14)
        
        features={
            'macd_12_26_9': macd,
            'rsi_14': rsi,
            'bollinger_upper_band': upper_band,
            'bollinger_middle_band': middle_band,
            'bollinger_lower_band': lower_band,
            'atr_14_period': atr,
            'sma_20_period': sma
        }
        return fifteen_min_interval, one_day_interval, features 
    
    def plot_market_data(self,data,title="Candlestick Chart with Volume",mav=(20,50)):
        # plot market data
        fig,ax = mpf.plot(data,type='candle',volume=True,style='yahoo',mav=mav,returnfig=True,figsize=(20,12),title=title)
        # return figure
        return fig

    def get_news(self):
        # get news
        pass

    def get_custom_market_data_with_indicators(self, interval: str, indicators: list, start_date: datetime = None):
        # Validate interval
        valid_intervals = self.crypto_client.valid_granularity
        if interval not in valid_intervals:
            raise ValueError(f"Interval {interval} is not supported. Choose from {valid_intervals}")

        # Validate indicators
        available_indicators = dir(ta)
        for indicator in indicators:
            if indicator not in available_indicators:
                raise ValueError(f"Indicator {indicator} is not available in TA-Lib")

        if start_date is None:
            start_date = datetime.now() - timedelta(days=3)

        # Fetch market data
        market_data = self.crypto_client.get_market_data(self.symbol, granularity=interval, start=start_date)

        # Calculate requested indicators
        calculated_indicators = {}
        for indicator in indicators:
            func = getattr(ta, indicator)
            # Assuming the indicator function takes 'close' prices as input
            calculated_indicators[indicator] = func(market_data['close'])

        return {
            'market_data': market_data,
            'indicators': calculated_indicators
        }

    def initialize_chat_assistant(self):
        """
        Initializes the OpenAI chat assistant with access to various tools for trading analysis.
        """
        # Define available tools
        tools = {
            'get_orderbook_data': self.get_orderbook_data,
            'get_technical_features': self.get_technical_features,
            'get_data_with_indicators': self.get_data_with_indicators,
            'get_news': self.get_news
        }

        # Create a chat session with OpenAI
        def chat(prompt):
            response = openai.ChatCompletion.create(
                model="gpt-4-vision",
                messages=[{"role": "system", "content": "You are a trading assistant with access to various market data tools."},
                          {"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response['choices'][0]['message']['content']

        return chat, tools

    def get_tools_description(self):
        """This function returns the tools available to the agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_orderbook_data",
                    "description": "Retrieve the order book data for a specific trading symbol, including aggregated asks and bids order books and order book features dictionary.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "price_level_increment": {
                                "type": "number",
                                "description": "The increment for price levels when aggregating the order book.",
                                "default": 0.5
                            }
                        },
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_market_data",
                    "description": "Extract 15-minute and 1-day market data and calculate predefined technical indicators for 15-minute time frame.",
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_custom_market_data_with_indicators",
                    "description": "Fetch market data with custom intervals and calculate specified technical indicators.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "interval": {
                                "type": "string",
                                "description": "The data interval for the market data. Valid intervals include 'ONE_MINUTE', 'FIVE_MINUTE', 'FIFTEEN_MINUTE', 'THIRTY_MINUTE', 'ONE_HOUR', 'TWO_HOUR', 'SIX_HOURS', 'ONE_DAY', etc."
                            },
                            "indicators": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of technical indicators to calculate, e.g., ['MACD', 'RSI', 'SMA']. Ensure the name of the indicator matches the name of the function in TA-Lib."
                            },
                            "start_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "The start date for retrieving market data. Defaults to 3 days ago if not provided."
                            }
                        },
                        "required": ["interval", "indicators"]
                    }
                }
            }
        ]

    def get_assistant_response(self, prompt):
        chat, tools = self.initialize_chat_assistant()
        # Use the chat function to get a response
        return chat(prompt)

if __name__ == "__main__":
    agent = TradingAgent(symbol="SOL-PERP-INTX")
    x = agent.get_market_data()
    # print(x[0])
    # print(x[0].info())
    fig,ax = mpf.plot(x[0].set_index("timestamp"),type='candle',volume=True,style='yahoo',mav=(20,50),figsize=(20,10),title="Candlestick Chart with Volume for 15 Min Intervals",returnfig=True)
    # save figure without background and tight layout
    fig.savefig('sol_perp_intx.png')

    # get orderbook data
    ob = agent.get_orderbook_data()
    print(ob)