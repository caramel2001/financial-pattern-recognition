from src.seasonality.seasonal import Seasonal
from src.data_client.fyers import FyersData
import pandas as pd
def main():
    # Assume access token geenrated already adn read from token.txt
    fyers = FyersData()
    # NSE:SBIN
    data  = fyers.get_historical_data("SBIN-EQ","NSE",interval="60") # hour
    data = pd.DataFrame(data['candles'],columns=['Date','Open','High','Low','Close','Volume'])
    data['Date'] = pd.to_datetime(data['Date'],unit='s')
    print(data.head())
    print(data.set_index('Date').resample("1D").count().head())
    # Seasonal Analysis
    seasonal = Seasonal(data=data.set_index('Date'),freq=7)

    analysis = seasonal.intraday_variance_analysis(period='H',log=False,plot=True)

if __name__ == "__main__":
    main()
