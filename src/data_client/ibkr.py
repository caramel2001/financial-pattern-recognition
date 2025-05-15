from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData
import threading
import time

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

    def run_app(self):
        # Start connection thread
        thread = threading.Thread(target=self.run)
        thread.start()

        # Give IB Gateway time to connect
        time.sleep(1)

        self.start()

        # Wait for data to complete
        while not self.data_end:
            time.sleep(1)

        self.disconnect()


if __name__ == "__main__":
    app = IBHistoricalDataApp()
    app.connect("127.0.0.1", 7497, clientId=1)
    app.run_app()
