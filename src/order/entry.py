import yfinance as yf   
import datetime

def find_avg_spread(ticker,days = 14):
    """Finds Average spread for a given ticker in the past "days" days"""
    start = datetime.datetime.now()
    since = start - datetime.timedelta(days = days)

    data = yf.download(ticker, start=since, end=start)
    data['spread'] = data['High'] - data['Low']
    spread_quantile = data['spread'].quantile(0.25)
    entry = data['Close'].iloc[-1] - data['spread'].quantile(0.25)
    return data['spread'].mean(),spread_quantile,entry

# Example usage
if __name__ == "__main__":
    print(find_avg_spread("SOFI"))