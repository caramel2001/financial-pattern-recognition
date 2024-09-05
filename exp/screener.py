from src.data_client.seeking_alpha import SeekingAlpha
from src.data_client.alpaca import Stock
from datetime import date,datetime,timedelta
import pandas as pd
from src.portfolio.alpaca import PaperFolio
from src.utils.config import settings
from alpaca.data.timeframe import TimeFrame,TimeFrameUnit
from alpaca.trading.enums import OrderSide
from loguru import logger

def screener():
    # screen = SeekingAlpha()
    # logger.debug("Getting screen stocks from Seeking Alpha")
    # screen_df = screen.get_screen_stocks()
    # #print(screen_df.head())
    # screen_df.to_csv(f"data/seeking_alpha_screen_{date.today()}.csv")
    # return screen_df
    screen_df = pd.read_csv(f"data/seeking_alpha_screen_{date.today()}.csv")
    return screen_df

def update_paper_portfolio(screen_df:pd.DataFrame):
    logger.debug("Getting paper portfolio")
    portfolio = PaperFolio(
    api_key=settings['ALPACA_API_KEY'],
    secret_key=settings['ALPACA_SECRET_KEY'],)
    logger.debug("Checking asset availability")
    available_assets = portfolio.check_asset_availability(screen_df['attributes.name'].tolist())
    logger.debug(f"Available assets: {sum(available_assets)} out of {len(available_assets)}")
    screen_df = screen_df.loc[available_assets]
    weights = 1/len(screen_df)
    logger.debug(f"New weight of each stock: {weights}")
    portfolio_value = float(portfolio.account.equity)
    # get current positions
    current_positions = portfolio.get_positions()
    current_weights = {position.symbol:position.market_value/portfolio_value for position in current_positions}
    
    # amount change weight to reach the new weight
    amount_change = {symbol:weights - current_weights.get(symbol,0) for symbol in screen_df['attributes.name']}
    # add stocks that are to be removed from the portfolio
    for symbol in current_weights.keys():
        if symbol not in screen_df['attributes.name'].tolist():
            amount_change[symbol] = -current_weights[symbol]
            
    logger.debug(f"Amount to change to acheive new weight: {amount_change}")

    # get limit price for each stock
    logger.debug("Getting limit price for each stock")
    stock_client = Stock(api_key=settings['ALPACA_API_KEY'],secret_key=settings['ALPACA_SECRET_KEY'], start_date=datetime.now()-timedelta(days=2),timeframe=TimeFrame(4,TimeFrameUnit.Hour))
    data = stock_client.get_data(screen_df['attributes.name'].tolist())

    limit_prices={}
    for i,j in data.data.items():
         #print(i)
         limit_prices[i] = get_limit_price(j)

    # submit orders
    for i in range(len(screen_df)):
        symbol = screen_df['attributes.name'].iloc[i]
        limit_price = round(limit_prices[symbol],2)
        qty = int((amount_change[symbol]*portfolio_value)/limit_price)
        if amount_change[symbol] == 0:
            logger.debug(f"No change in portoflio weight for {symbol}")
            continue
        if qty < 0:# sell order
            logger.debug(f"Creating sell market order for {symbol}")
            side = OrderSide.SELL
            qty = abs(qty)
            order = portfolio.create_market_order(symbol,qty,side)
            logger.debug(f"Order submitted for {symbol}: {order}")
        else:
            logger.debug(f"Creating buy limit order for {symbol} at {limit_price}")
            side = OrderSide.BUY
            order = portfolio.create_limit_order(symbol,qty,side,limit_price)
            logger.debug(f"Order submitted for {symbol}: {order}")


def get_limit_price(data:dict):
    # TODO improve this logic this way the limit price will lead to buying stocks that behave poorly next day.
    price_df = pd.DataFrame()
    price_df['open']  = [x.open for x in data]
    price_df['close'] = [x.close for x in data]
    price_df['high'] = [x.high for x in data]
    price_df['low'] = [x.low for x in data]
    price_df['volume'] = [x.volume for x in data]
    price_df['timestamp'] = [x.timestamp for x in data]
    price_df['var'] = abs(price_df['high'] - price_df['low'])
    price_df.set_index('timestamp',inplace=True)
    #print(price_df)
    return price_df.iloc[-1]['close'] - price_df['var'].mean()
   

if __name__=="__main__":
    screen_df =screener()
    update_paper_portfolio(screen_df)