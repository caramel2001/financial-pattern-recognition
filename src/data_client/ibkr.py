from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData
import threading
import time
import argparse
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

class IBHistoricalDataApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        self.historical_data = []
        self.data_end = False

    def historicalData(self, reqId, bar: BarData):
        print(f"HistoricalData: Date: {bar.date}, Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}")
        self.historical_data.append(bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        print(f"HistoricalDataEnd. ReqId: {reqId}, from {start} to {end}")
        self.data_end = True

    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderRejectJson=""):
        if errorCode not in [2104, 2106, 2158]:
            print(f"Error. ReqId: {reqId}, Time: {errorTime}, Code: {errorCode}, Msg: {errorString}")
            if advancedOrderRejectJson:
                print(f"Advanced Order Reject JSON: {advancedOrderRejectJson}")


    def start(self):
        # Define your contract (example: AAPL stock on SMART)
        contract = Contract()
        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        # Request historical data
        queryTime = (time.strftime("%Y%m%d-%H:%M:%S"))
        self.reqHistoricalData(reqId=1, 
                               contract=contract,
                               endDateTime=queryTime,
                               durationStr="2 D",
                               barSizeSetting="5 mins",
                               whatToShow="TRADES",
                               useRTH=1,
                               formatDate=1,
                               keepUpToDate=False,
                               chartOptions=[])

    def get_volatility_breakout_data(self):
        # Data since 2018
        # 1min interval
        # symbols
        # SPY (SPDR S&P 500 ETF Trust)
        # IWM (iShares Russell 2000 ETF)
        # QQQ (Invesco QQQ Trust)
        # GLD (SPDR Gold Shares)
        # USO (United States Oil Fund)
        # DIA (SPDR Dow Jones Industrial Average ETF Trust)
        contract_configs = [
            # ("SPY", "STK", "SMART", "USD"),
            # ("IWM", "STK", "SMART", "USD"),
            # ("QQQ", "STK", "SMART", "USD"),
            # ("GLD", "STK", "SMART", "USD"),
            # ("USO", "STK", "SMART", "USD"),
            ("DIA", "STK", "SMART", "USD")
        ]
        for symbol, secType, exchange, currency in contract_configs:
            contract = Contract()
            contract.symbol = symbol
            contract.secType = secType
            contract.exchange = exchange
            contract.currency = currency

            # Request historical data for each contract
            queryTime = (time.strftime("%Y%m%d-%H:%M:%S"))
            self.reqHistoricalData(reqId=1, 
                                   contract=contract,
                                   endDateTime=queryTime,
                                   durationStr="30 D",
                                   barSizeSetting="1 min",
                                   whatToShow="TRADES",
                                   useRTH=1,
                                   formatDate=1,
                                   keepUpToDate=False,
                                   chartOptions=[])
    
    def run_app(self):
        # Start connection thread
        thread = threading.Thread(target=self.run)
        thread.start()

        # Give IB Gateway time to connect
        time.sleep(1)

        # self.start()
        self.get_volatility_breakout_data()

        # Wait for data to complete
        while not self.data_end:
            time.sleep(1)

        self.disconnect()




class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.data_event = threading.Event()
        self.request_complete = False

    def historicalData(self, reqId, bar):
        try:
            # Parse timestamp with timezone
            date_str, tz_str = bar.date.split(' US/')
            naive_dt = datetime.strptime(date_str, "%Y%m%d %H:%M:%S")
            tz = pytz.timezone(f'US/{tz_str}')
            localized_dt = tz.localize(naive_dt)
            utc_dt = localized_dt.astimezone(pytz.utc)
            print(f"Received data for {bar.date}: Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}")
            self.data.append({
                'timestamp': utc_dt,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume
            })
        except Exception as e:
            print(f"Error processing bar: {e}")

    def historicalDataEnd(self, reqId, start, end):
        self.request_complete = True
        self.data_event.set()

    def run_loop(self):
        self.run()

def main(args):
    # Initialize API
    app = IBapi()
    app.connect('127.0.0.1', 7497, clientId=1)

    # Connection timeout handling
    connect_timeout = 10
    start_time = time.time()
    while not app.isConnected():
        if time.time() - start_time > connect_timeout:
            raise Exception("Connection timeout")
        time.sleep(0.1)

    # Start API thread
    api_thread = threading.Thread(target=app.run_loop, daemon=True)
    api_thread.start()
    time.sleep(1)  # Stabilization period

    # Contract setup
    contract = Contract()
    contract.symbol = args.ticker
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'

    # Date handling
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    # Loop through requests
    current_date = start_date
    while current_date <= end_date:
        end_date_str = current_date.strftime("%Y%m%d 23:59:59 US/Eastern")
        next_date = current_date + timedelta(days=1)

        # Request parameters
        app.reqHistoricalData(
            reqId=1,
            contract=contract,
            endDateTime=end_date_str,
            durationStr='1 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=1,  # Use all available data, not just Regular Trading Hours
            formatDate=1,
            keepUpToDate=False,
            chartOptions=[]
        )

        # Wait for data with timeout
        if not app.data_event.wait(30):
            print(f"Timeout waiting for data on {current_date.strftime('%Y-%m-%d')}")
            return

        # Process and save data
        if app.data:
            df = pd.DataFrame(app.data)
            df.set_index('timestamp', inplace=True)

            # Create directory structure
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m")
            filename = f"{current_date.strftime('%Y-%m-%d')}.parquet.snappy"
            storage_dir = f"{os.environ['HOME']}/Desktop/2024projects/PatternRecognition/data/ibkr/{args.ticker}/{year}/{month}"
            os.makedirs(storage_dir, exist_ok=True)

            # Save with partitioning
            df.to_parquet(
                os.path.join(storage_dir, filename),
                compression='snappy',
                index=True
            )
            print(f"Saved {len(df)} rows for {current_date.strftime('%Y-%m-%d')}")

            # Clear data for next request
            app.data = []
            app.data_event.clear()
        else:
            print("NO DATA!")

        current_date = next_date

    app.disconnect()
    api_thread.join(timeout=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Historical Data Downloader')
    parser.add_argument('--ticker', type=str, required=True,
                      help='Stock ticker symbol')
    parser.add_argument('--start-date', type=str, required=False, default='2024-01-01',
                      help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', type=str, required=False, default='2025-07-01',
                      help='End date in YYYY-MM-DD format')
    args = parser.parse_args()

    try:
        main(args)
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)

# if __name__ == "__main__":
#     app = IBHistoricalDataApp()
#     app.connect("127.0.0.1", 7497, clientId=1)
#     app.run_app()
