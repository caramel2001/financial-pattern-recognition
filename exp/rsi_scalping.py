from datetime import datetime
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# get current file path
from binance.client import Client
import joblib
import pandas as pd
import pandas_ta as ta
from tqdm import tqdm
import requests
from src.utils.config import settings
import asyncio
import joblib
import numpy as np
from scipy import linalg as la

# save all loguru logs to a file
from loguru import logger


log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "PCA_RSI_STRATEGY.log")
logger.add(log_file, rotation="10 MB", encoding="utf8")
tqdm.pandas()


# Telegram bot setup
TELEGRAM_BOT_TOKEN = settings['TELEBOT_KEY']
TELEGRAM_CHAT_ID = settings['TELEBOT_CHATID']


# parameters
rsi_lbs = list(range(2, 30))
train_size = 24 * 365 * 2
step_size = 24 * 365
n_components = 3
lookahead = 3
parameters_file = "pca_rsi_params.pkl"
parameters_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", parameters_file)
print(f"Parameters file path: {parameters_file}")

def pca_linear_model(x, y, n_components):
        means = x.mean()
        x -= means
        x = x.dropna()

        cov = np.cov(x, rowvar=False)
        evals, evecs = la.eigh(cov)
        idx = np.argsort(evals)[::-1]
        evecs = evecs[:, idx]

        model_data = pd.DataFrame()
        for j in range(n_components):
            model_data['PC' + str(j)] = pd.Series(np.dot(x, evecs[j]), index=x.index)

        cols = list(model_data.columns)
        model_data['target'] = y
        model_coefs = la.lstsq(model_data[cols], y)[0]
        model_data['pred'] = np.dot(model_data[cols], model_coefs)

        l_thresh = model_data['pred'].quantile(0.98)
        s_thresh = model_data['pred'].quantile(0.02)

        return model_coefs, evecs, means, l_thresh, s_thresh

def send_telegram_message(message: str):
    """Sends a message to the configured Telegram chat."""
    print("Sending Telegram message:", message)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

def get_processed_data(symbol, interval, limit=100):
    df = get_ohlcv(symbol, interval, limit)
    df = df.astype(float)
    if df.empty:
        return pd.DataFrame()

    # Calculate RSI values
    rsis = pd.DataFrame()
    for lb in rsi_lbs:
        rsis[lb] = ta.rsi(df['close'], lb)

    # Prepare target variable
    tar = np.log(df['close']).diff(lookahead).shift(-lookahead)
    
    # Drop NaNs
    rsis['tar'] = tar
    rsis.dropna(inplace=True)
    
    target = rsis['tar']
    rsis.drop('tar', axis=1, inplace=True)
    return df,rsis,target

def get_params(df:pd.DataFrame,target:pd.Series,rsi_lbs:list = rsi_lbs, lookahead:int = 3,n_components:int=3, parameters_file:str=parameters_file):
    """Generates PCA-RSI signals based on the given DataFrame."""

    # read the model parameters from json file 
    params_file = os.path.join(os.path.dirname(__file__), parameters_file)
    if os.path.exists(params_file):
        logger.info(f"Loading PCA-RSI parameters from {params_file}")
        params = joblib.load(params_file)
        means = params['means']
        l_thresh = params['l_thresh']
        s_thresh = params['s_thresh']
        model_coefs = params['model_coefs']
        evecs = params['evecs']
        n_components = params['n_components']
        rsi_lbs = params['rsi_lbs']
        lookahead = params['lookahead']
        # Check if the model parameters are still valid
        expiration_date = datetime.strptime(params['expiration_date'], '%Y-%m-%d')
        if datetime.now() > expiration_date:
            logger.warning("PCA-RSI parameters have expired, refitting the model.")
            # get last two years of data
            start_date = df.index[-1] - pd.DateOffset(years=2)
            
            # Fit the model again if the parameters are expired
            model_coefs, evecs, means, l_thresh, s_thresh = pca_linear_model(df, target, n_components)
            # Save the updated parameters to a file
            params = {
                'means': means,
                'l_thresh': l_thresh,
                's_thresh': s_thresh,
                'model_coefs': model_coefs,
                'evecs': evecs,
                'n_components': n_components,
                'rsi_lbs': rsi_lbs,
                'lookahead': lookahead,
                # expiration date for the model parameters today + step_size days
                'expiration_date': (datetime.now() + timedelta(hours=step_size)).strftime('%Y-%m-%d')
            }
            joblib.dump(params, params_file)
    else:
        # If no parameters file exists, fit the model
        model_coefs, evecs, means, l_thresh, s_thresh = pca_linear_model(df, target, n_components)
        # Save the model parameters to a file
        params = {
            'means': means,
            'l_thresh': l_thresh,
            's_thresh': s_thresh,
            'model_coefs': model_coefs,
            'evecs': evecs,
            'n_components': n_components,
            'rsi_lbs': rsi_lbs,
            'lookahead': lookahead,
            # expiration date for the model parameters today + step_size days
            'expiration_date': (datetime.now() + timedelta(days=step_size)).strftime('%Y-%m-%d')
        }
        joblib.dump(params, parameters_file)

    return params

def get_signal(rsis:pd.DataFrame,model_params:dict):
    rsi_means = model_params['means']
    evecs = model_params['evecs']
    model_coefs = model_params['model_coefs']
    l_thresh = model_params['l_thresh']
    s_thresh = model_params['s_thresh']
    n_components = model_params['n_components']
    # curr_row = rsis.iloc[i] - rsi_means
    # vec = np.array([np.dot(curr_row, evecs[j]) for j in range(n_components)])
    # curr_pred = np.dot(vec, model_coefs)
    
    curr_row = rsis.iloc[-1] - rsi_means
    vec = np.array([np.dot(curr_row, evecs[j]) for j in range(n_components)])
    curr_pred = np.dot(vec, model_coefs)
    print(f"Current RSI PCA Prediction: {curr_pred}")
    if curr_pred > l_thresh:
        return 1 # long
    elif curr_pred < s_thresh:
        return -1 # short
    return 0 # neutral

def fetch_ohlcv_async(symbol, interval, limit=100,start_date=None, end_date=None):
    """Fetch OHLCV data asynchronously."""
    
    client = Client(api_key=settings['BINANCE_API_KEY'], api_secret=settings['BINANCE_SECRET_KEY'])
    # Fetch klines (OHLCV data) from Binance Futures
    if limit <= 1500:
        candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit, startTime=start_date, endTime=end_date)
        df = pd.DataFrame(candles)
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 
                    'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    else:
        # If limit is greater than 1500, fetch in chunks
        candles = []
        for i in tqdm(range(0, limit, 1500)):
            chunk = client.futures_klines(symbol=symbol, interval=interval, limit=min(1500, limit - i),endTime=end_date)
            # new start_time for the next chunk
            if chunk:
                end_date = chunk[0][0] - 1
            candles.extend(chunk)
        df = pd.DataFrame(candles)
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 
                    'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)
    return df

def fetch_current_price_async(symbol):
    """Fetches the most recent price for the given symbol asynchronously."""
    client = Client(api_key=settings['BINANCE_API_KEY'], api_secret=settings['BINANCE_SECRET_KEY'])
    ticker = client.futures_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def get_ohlcv(symbol, interval, limit=100):
    """Wrapper to run async fetch_ohlcv."""
    return fetch_ohlcv_async(symbol, interval, limit)

def get_current_price(symbol):
    """Wrapper to run async fetch_current_price."""
    return fetch_current_price_async(symbol)


def main():
    logger.debug(f"Running trading job at {datetime.now()}")
    symbol="ETHUSDT"
    df,rsis,target = get_processed_data(symbol, "1h",limit=10000)
    params = get_params(rsis,target)
    signal = get_signal(rsis, params)

    current_price = get_current_price(symbol)

    if signal == 1:
        message = f"RSI Scalping : Long signal for {symbol} at price {current_price:.2f} at {datetime.now()}"
        logger.info(message)
        send_telegram_message(message)
    elif signal == -1:
        message = f"RSI Scalping : Short signal for {symbol} at price {current_price:.2f} at {datetime.now()}"
        logger.info(message)
        send_telegram_message(message)
    else:
        message = f"No signal for {symbol} at price {current_price:.2f} at {datetime.now()}"
        logger.info(message)

if __name__ == "__main__":
    # Configure logger to write to a file
    logger.info("Starting PCA-RSI scalping job")
    main()
