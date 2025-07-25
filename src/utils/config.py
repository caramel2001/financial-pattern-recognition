from pathlib import Path
from os import getenv

# from base import load_env
from dotenv import load_dotenv

# get path for the this file
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR.joinpath(".env"))

settings = {
    "QUANDL": getenv("QUANDL"),
    "STOCK_DATA": getenv("STOCK_DATA"),
    "NEWSAPI_KEY": getenv("NEWSAPI_KEY"),
    "ALPHAVANTAGE_KEY": getenv("ALPHAVANTAGE_KEY"),
    "BING_KEY": getenv("BING_KEY"),
    "ALPACA_API_KEY": getenv("ALPACA_API_KEY"),
    "ALPACA_SECRET_KEY": getenv("ALPACA_SECRET_KEY"),
    "FYERS_CLIENT_ID": getenv("FYERS_CLIENT_ID"),
    "FYERS_SECRET": getenv("FYERS_SECRET"),
    "FYERS_REDIRECT_URI": getenv("FYERS_REDIRECT_URI"),
    "FYERS_AUTH_CODE": getenv("FYERS_AUTH_CODE"),
    "FYERS_PIN": getenv("FYERS_PIN"),
    "FINNHUB_API_KEY": getenv("FINNHUB_API_KEY"),
    "OPENAI_API_KEY": getenv("OPENAI_API_KEY"),
    "COINBASE_API_KEY": getenv("COINBASE_API_KEY"),
    "COINBASE_SECRET_KEY": getenv("COINBASE_SECRET_KEY"),
    "MONGO_URI": getenv("MONGO_URI"),
    "COSMOS_URI": getenv("COSMOS_URI"),
    "COSMOS_KEY": getenv("COSMOS_KEY"),
    "COINBASE_API_KEY_2": getenv("COINBASE_API_KEY_2"),
    "COINBASE_SECRET_KEY_2": getenv("COINBASE_SECRET_KEY_2"),
    "BINANCE_TESTNET_API_KEY": getenv("BINANCE_TESTNET_API_KEY"),
    "BINANCE_TESTNET_SECRET_KEY": getenv("BINANCE_TESTNET_SECRET_KEY"),
    "BINANCE_API_KEY": getenv("BINANCE_API_KEY"),
    "BINANCE_SECRET_KEY": getenv("BINANCE_SECRET_KEY"),
    "TELEBOT_KEY": getenv("TELEBOT_KEY"),
    "TELEBOT_CHATID": getenv("TELEBOT_CHATID"),
    "LOCAL_MONGO_URI": getenv("LOCAL_MONGO_URI"),
    "GEMINI_KEY" : getenv("GEMINI_KEY"),
}
