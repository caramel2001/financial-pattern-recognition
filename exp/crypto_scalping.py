from datetime import datetime
from datetime import datetime, timedelta
import sys
import os
# get current file path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from binance.client import Client
import joblib
import pandas as pd
import pandas_ta as ta
from tqdm import tqdm
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
from src.feature.overbar import Alpha158
from src.utils.config import settings
import asyncio
# save all loguru logs to a file
from loguru import logger

log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "strategy.log")
logger.add(log_file, rotation="10 MB", encoding="utf8")
tqdm.pandas()


# Telegram bot setup
TELEGRAM_BOT_TOKEN = settings['TELEBOT_KEY']
TELEGRAM_CHAT_ID = settings['TELEBOT_CHATID']

def send_telegram_message(message: str):
    """Sends a message to the configured Telegram chat."""
    print("Sending Telegram message:", message)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

def get_processed_data(symbol, interval, limit=100):
    df = get_ohlcv(symbol, interval, limit)
    df = df.astype(float)
    df["EMA_slow"]=ta.ema(df.close, length=50)
    df["EMA_fast"]=ta.ema(df.close, length=30)
    df['RSI']=ta.rsi(df.close, length=10)
    my_bbands = ta.bbands(df.close, length=15, std=1.5)
    df['ATR']=ta.atr(df.high, df.low, df.close, length=7)
    df=df.join(my_bbands)
    df.reset_index(inplace=True)
    alpha = Alpha158(df,basic=True)
    df = alpha.alpha158()
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "best_decision_tree_model_5.pkl")
    scaler_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "best_decision_tree_model_5_scaler.pkl")
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    X = df.drop(["date"],axis=1)
    if "MLSignal" in X.columns:
        X = X.drop(["MLSignal"],axis=1)
    X = X.rename(columns={"open": "Open", "close": "Close", "high": "High", "low": "Low","volume": "Volume"})
    # X.reset_index(inplace=True)
    X = scaler.transform(X)
    signal = model.predict(X)
    signal_prob = model.predict_proba(X)
    df['MLSignal'] = signal
    df['MLSignalProb'] = [max(i) for i in signal_prob]
    
    return df

def get_signals(df:pd.DataFrame):
    df_slice = df.reset_index().copy()
    def ema_signal(current_candle, backcandles):
        # Get the range of candles to consider
        start = max(0, current_candle - backcandles)
        end = current_candle
        relevant_rows = df_slice.iloc[start:end]

        # Check if all EMA_fast values are below EMA_slow values
        if all(relevant_rows["EMA_fast"] < relevant_rows["EMA_slow"]):
            return 1
        elif all(relevant_rows["EMA_fast"] > relevant_rows["EMA_slow"]):
            return 2
        else:
            return 0
    def total_signal(df, current_candle, backcandles):
        if (ema_signal(current_candle, backcandles)==2
            and df.close[current_candle]<=df['BBL_15_1.5'][current_candle] and df.MLSignal[current_candle]==True #and df.MLSignalProb[current_candle]>0.55
            #and df.RSI[current_candle]<60
            ):
                return 2
        if (ema_signal(current_candle, backcandles)==1
            and df.close[current_candle]>=df['BBU_15_1.5'][current_candle] and df.MLSignal[current_candle]==True #and df.MLSignalProb[current_candle]>0.55
            #and df.RSI[current_candle]>40
            ):
        
                return 1
        return 0

    df.dropna(inplace=True)
    df['TotalSignal'] = df.progress_apply(lambda row: total_signal(df, row.name, 7), axis=1)
    return df


async def fetch_ohlcv_async(symbol, interval, limit=100):
    """Fetch OHLCV data asynchronously."""
    client = Client(api_key=settings['BINANCE_API_KEY'], api_secret=settings['BINANCE_SECRET_KEY'])
    candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(candles)
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 
                  'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    df.set_index("date", inplace=True)
    return df

async def fetch_current_price_async(symbol):
    """Fetches the most recent price for the given symbol asynchronously."""
    client = Client(api_key=settings['BINANCE_API_KEY'], api_secret=settings['BINANCE_SECRET_KEY'])
    ticker = client.futures_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def get_ohlcv(symbol, interval, limit=100):
    """Wrapper to run async fetch_ohlcv."""
    return asyncio.run(fetch_ohlcv_async(symbol, interval, limit))

def get_current_price(symbol):
    """Wrapper to run async fetch_current_price."""
    return asyncio.run(fetch_current_price_async(symbol))


def trading_job():
    logger.debug(f"Running trading job at {datetime.now()}")
    symbol="WLDUSDT"
    df = get_processed_data(symbol, "5m")
    df = get_signals(df)
    df.set_index("date", inplace=True)
    # Get the current UTC time
    now = datetime.utcnow()
    # Calculate the last completed 5-minute candle time
    # Floor to 5 min, then subtract 1 period to get the completed one
    last_candle_time = (now - timedelta(minutes=now.minute % 5,
                                        seconds=now.second,
                                        microseconds=now.microsecond)) - timedelta(minutes=5)
    # Select the candle with exact timestamp
    if last_candle_time in df.index:
        last_candle = df.loc[last_candle_time]
    else:
        logger.error(f"No candle found for {last_candle_time}. Check your data range or refresh data.")
        return
    slcoef = 1.1
    TPSLRatio = 1.5
    slatr = slcoef * last_candle.ATR
    signal = last_candle.TotalSignal
    current_price = get_current_price(symbol)  # Get the most recent price

    if signal == 2:
        sl1 = current_price - slatr
        tp1 = current_price + slatr * TPSLRatio
        send_telegram_message(f"Buy signal detected!\nTime: {datetime.now()}\nPrice: {current_price}\nStoploss: {sl1}\nTake Profit: {tp1} \ndataframe last timestamp: {last_candle_time}")
        logger.debug(f"Buy signal detected at {datetime.now()}")
    elif signal == 1:
        sl1 = current_price + slatr
        tp1 = current_price - slatr * TPSLRatio
        send_telegram_message(f"Sell signal detected!\nTime: {datetime.now()}\nPrice: {current_price}\nStoploss: {sl1}\nTake Profit: {tp1}  \ndataframe last timestamp: {last_candle_time}")
        logger.debug(f"Sell signal detected at {datetime.now()}")
    else:
        send_telegram_message(f"No signal detected!\nTime: {datetime.now()}\nPrice: {current_price} \ndataframe last timestamp: {last_candle_time}")
        logger.debug(f"No signal detected at {datetime.now()}")

    # write new signal in a csv file
    df.loc[last_candle_time].to_frame().transpose().to_csv(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\logs\MLScalping.csv', mode='a', header=True)
# Schedule the job to run every 5 minutes using a cron expression
# scheduler = BlockingScheduler()
# scheduler.add_job(
#     trading_job,
#     'cron',
#     hour='0-23',
#     minute='1,6,11,16,21,26,31,36,41,46,51,56',
#     start_date='2025-04-16 12:00:00',
#     misfire_grace_time=60
# )

# print("Starting scheduler...")
# scheduler.start()
trading_job()