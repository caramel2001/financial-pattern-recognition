# Features based on OHLCV data 
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


class OverbarFeature:
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def technical_indicators(self):
        pass



class Alpha158:
    def __init__(self, data: pd.DataFrame, basic: bool = False, windows : list = [5, 10, 20, 30, 60]):
        self.data = data
        self.basic = basic
        self.windows = windows

    def alpha158(self):
        df = self.data.copy()
        df["zopen"] = df["open"] / df["close"] - 1
        df["zhigh"] = df["high"] / df["close"] - 1
        df["zlow"] = df["low"] / df["close"] - 1
        df["zadjcp"] = df["adjclose"] / df["close"] - 1
        df["zclose"] = (df.close /(df.close.rolling(2).sum() - df.close)) - 1
        df["zd_5"] = (df.close.rolling(5).sum() /5) / df.close - 1
        df["zd_10"] = (df.close.rolling(10).sum() /10) / df.close - 1
        df["zd_15"] = (df.close.rolling(15).sum() /15) / df.close - 1
        df["zd_20"] = (df.close.rolling(20).sum() /20) / df.close - 1
        df["zd_25"] = (df.close.rolling(25).sum() /25) / df.close - 1
        df["zd_30"] = (df.close.rolling(30).sum() /30) / df.close - 1
        df["zd_60"] = (df.close.rolling(60).sum() /60) / df.close-1  

        if self.basic == False:  
            df['KMID'] = (df['close'] + df['open']) / df['open']
            df['KLEN'] = (df['high'] - df['low']) / df['open']
            df['KMID2'] = (df['close'] - df['open']) / (df['high'] - df['low'] + 1e-12)
            df['KUP'] = (df['high']-df[['close', 'open']].max(axis=1)) / df['open']
            df['KUP2'] = (df['high']-df[['close', 'open']].max(axis=1)) / (df['high'] - df['low'] + 1e-12)
            df['KLOW'] = (df[['close', 'open']].min(axis=1)-df['low']) / df['open']
            df['KLOW2'] = (df[['close', 'open']].min(axis=1)-df['low']) / (df['high'] - df['low'] + 1e-12)
            df['KSFT'] = (2*df['close']-df['high']-df['low']) / df['open']
            df['KSFT2'] = (2*df['close']-df['high']-df['low']) / (df['high'] - df['low'] + 1e-12)

            features = []
            for w in self.windows:
                # Calculate all the features and store in a temporary DataFrame
                temp_df = pd.DataFrame({
                    #ROC
                    # https://www.investopedia.com/terms/r/rateofchange.asp
                    # Rate of change, the price change in the past d days, divided by latest close price to remove unit
                    f'ROC{w}': df['close'].shift(w) / df['close'],
                    # MA 
                    # https://www.investopedia.com/ask/answers/071414/whats-difference-between-moving-average-and-weighted-moving-average.asp
                    # Simple Moving Average, the simple moving average in the past d days, divided by latest close price to remove unit 
                    f'MA{w}': df['close'].rolling(window=w).mean() / df['close'],
                    # STD
                    # The standard diviation of close price for the past d days, divided by latest close price to remove unit
                    f'STD{w}': df['close'].rolling(window=w).std() / df['close'],
                    # BETA
                    # The rate of close price change in the past d days, divided by latest close price to remove unit 
                    # For example, price increase 10 dollar per day in the past d days, then Slope will be 10.
                    f'BETA{w}': df['close'].rolling(window=w).apply(lambda x: np.polyfit(range(w), x, 1)[0]) / df['close'],
                    # MAX
                    # The max price for past d days, divided by latest close price to remove unit
                    f'MAX{w}': df['close'].rolling(window=w).max() / df['close'],
                    # MIN
                    # The low price for past d days, divided by latest close price to remove unit
                    f'MIN{w}': df['close'].rolling(window=w).min() / df['close'],
                    # QTLU
                    # Used with MIN and MAX
                    # The 80% quantile of past d day's close price, divided by latest close price to remove unit
                    f'QTLU{w}': df['close'].rolling(window=w).quantile(0.8) / df['close'],
                    # QTLD
                    # The 20% quantile of past d day's close price, divided by latest close price to remove unit
                    f'QTLD{w}': df['close'].rolling(window=w).quantile(0.2) / df['close'],
                    # RANK
                    # Get the percentile of current close price in past d day's close price.
                    f'RANK{w}': df['close'].rolling(window=w).rank(),
                    # IMAX
                    # The number of days between current date and previous highest price date.
                    # Part of Aroon Indicator https://www.investopedia.com/terms/a/aroon.asp
                    # The indicator measures the time between highs and the time between lows over a time period.
                    # The idea is that strong uptrends will regularly see new highs, and strong downtrends will regularly see new lows.
                    f'IMAX{w}': df['high'].rolling(w).apply(np.argmax) / w,
                    # IMIN
                    # The number of days between current date and previous lowest price date.
                    # Part of Aroon Indicator https://www.investopedia.com/terms/a/aroon.asp
                    # The indicator measures the time between highs and the time between lows over a time period.
                    # The idea is that strong uptrends will regularly see new highs, and strong downtrends will regularly see new lows.
                    f'IMIN{w}': df['low'].rolling(w).apply(np.argmax) / w,
                    # CORR
                    # The correlation between absolute close price and log scaled trading volume
                    f'CORR{w}': df['close'].rolling(window=w).corr(np.log(df['volume'] + 1)),
                    # CORD
                    # The correlation between price change ratio and volume change ratio
                    f'CORD{w}': df['close'].pct_change(periods=w).rolling(window=w).corr(np.log(df['volume'].pct_change(periods=w)+1)),
                    # CNTP
                    # The percentage of days in past d days that price go up.
                    f'CNTP{w}': (df['close'].pct_change(1).gt(0)).rolling(window=w).mean(),
                    # CNTN
                    # The percentage of days in past d days that price go down.
                    f'CNTN{w}': (df['close'].pct_change(1).lt(0)).rolling(window=w).mean(),
                    # VMA
                    # Simple Volume Moving average: https://www.barchart.com/education/technical-indicators/volume_moving_average
                    f'VMA{w}': df["volume"].rolling(window=w).mean() / (df["volume"] + 1e-12),
                    # VSTD
                    # The standard deviation for volume in past d days.
                    f'VSTD{w}': df["volume"].rolling(window=w).std() / (df["volume"] + 1e-12)
                })

                # Combine all features for the window `w` with the original DataFrame
                features.append(temp_df)

            df = pd.concat([df]+features, axis=1)

            for w in self.windows:                
                #RSQR
                # The R-sqaure value of linear regression for the past d days, represent the trend linear
                x = pd.Series(range(1, w + 1))
                y = df['close'][-w:]
                x = x.values.reshape(-1, 1)
                y = y.values.reshape(-1, 1)
                reg = LinearRegression().fit(x, y)
                df[f'RSQR{w}'] = reg.score(x, y)
                
                #RESI
                # The redisdual for linear regression for the past d days, represent the trend linearity for past d days.
                resi = y - reg.predict(x)
                df[f'RESI{w}'] = resi.mean()
      
                df['ret1'] = df['close'].pct_change(1)
                df['abs_ret1'] = np.abs(df['ret1'])
                df['pos_ret1'] = df['ret1']
                df.loc[df['pos_ret1'].lt(0),'pos_ret1'] = 0
                
                # RSV
                # Represent the price position between upper and lower resistent price for past d days.
                df[f'RSV{w}'] = (df['close'] - df['MIN' + str(w)]) / (df['MAX' + str(w)] - df['MIN' + str(w)] + 1e-12)
                
                #IMXD
                # The time period between previous lowest-price date occur after highest price date.
                # Large value suggest downward momemtum.
                df['IMXD' + str(w)] = ((df['IMAX' + str(w)] - df['IMIN' + str(w)])) / w

                #CNTD
                # The diff between past up day and past down day
                df[f'CNTD{w}'] = df[f'CNTP{w}'] - df[f'CNTN{w}']

                #SUMP
                # The total gain / the absolute total price changed
                # Similar to RSI indicator. https://www.investopedia.com/terms/r/rsi.asp
                df[f'SUMP{w}'] =df['pos_ret1'].rolling(w).sum()/ (df['abs_ret1'].rolling(w).sum() + 1e-12)
                
                #SUMN
                # The total lose / the absolute total price changed
                # Can be derived from SUMP by SUMN = 1 - SUMP
                # Similar to RSI indicator. https://www.investopedia.com/terms/r/rsi.asp
                df[f'SUMN{w}'] = 1 - df[f'SUMP{w}']
                
                #SUMD
                # The diff ratio between total gain and total lose
                # Similar to RSI indicator. https://www.investopedia.com/terms/r/rsi.asp
                df[f'SUMD{w}'] = 2 * df[f'SUMP{w}'] - 1

                #WVMA
                # The volume weighted price change volatility
                price_change = abs(df["close"] / df["close"].shift(1) - 1)
                df[f"WVMA{w}"] = (price_change * df["volume"]).rolling(window=w).std() / (price_change * df["volume"]).rolling(window=w).mean().add(1e-12)
                
                #VSUMP
                # The total volume increase / the absolute total volume changed
                volume_change = df["volume"] - df["volume"].shift(1)
                df[f"VSUMP{w}"] = volume_change.rolling(window=w).apply(lambda x: sum(x[x > 0])) / \
                      (abs(volume_change).rolling(window=w).sum() + 1e-12)
                # VSUMN
                # The total volume increase / the absolute total volume changed
                # Can be derived from VSUMP by VSUMN = 1 - VSUMP
                volume_change = df["volume"] - df["volume"].shift(1)
                df[f"VSUMN{w}"] = 1 - (volume_change.rolling(window=w).apply(lambda x: sum(x[x > 0])) / \
                           (abs(volume_change).rolling(window=w).sum() + 1e-12))
               
                # VSUMD
                # The diff ratio between total volume increase and total volume decrease
                # RSI indicator for volume
                volume_change = df["volume"] - df["volume"].shift(1)
                df[f"VSUMD{w}"] = (volume_change.rolling(window=w).apply(lambda x: sum(x[x > 0])) - volume_change.rolling(window=w).apply(lambda x: sum(x[x < 0]))) / \
                      (abs(volume_change).rolling(window=w).sum() + 1e-12)
                
            df.drop(columns=['ret1', 'abs_ret1', 'pos_ret1'], inplace=True)   

        return df

if __name__ == "__main__":
    # get data from yahoofinance
    import yfinance as yf
    data = yf.download("AAPL", start="2021-01-01")
    data.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adjclose",
            "Volume": "volume",
        },
        inplace=True,
    )
    print(data.head())
    alpha = Alpha158(data)
    df = alpha.alpha158()
    print(df.shape)
                

