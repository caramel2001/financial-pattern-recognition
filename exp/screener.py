from src.data_client.seeking_alpha import SeekingAlpha
from src.data_client.alpaca import Stock
from datetime import date,datetime,timedelta
import pandas as pd
from src.portfolio.alpaca import PaperFolio
from src.utils.config import settings
from src.portfolio.optimize import Optimizer
from alpaca.data.timeframe import TimeFrame,TimeFrameUnit
from alpaca.trading.enums import OrderSide
from loguru import logger

def screener():
    screen = SeekingAlpha()
    # logger.debug("Getting screen stocks from Seeking Alpha")
    # screen_df = screen.get_screen_stocks()
    # #print(screen_df.head())
    # screen_df.to_csv(f"data/seeking_alpha_screen_{date.today()}.csv")
    screen_df = pd.read_csv(f"data/seeking_alpha_screen_{date.today()}.csv")

    return screen_df

def get_optimized_portfolio(screen_df:pd.DataFrame,port_val:float):
    opt = Optimizer(screen_df['attributes.name'].tolist())
    logger.debug("Optimizing portfolio")
    weights,_ = opt.get_weights(port_val)
    return weights


def update_paper_portfolio(screen_df:pd.DataFrame):
    logger.debug("Getting paper portfolio")
    portfolio = PaperFolio(
    api_key=settings['ALPACA_API_KEY'],
    secret_key=settings['ALPACA_SECRET_KEY'],)
    logger.debug("Checking asset availability")
    available_assets = portfolio.check_asset_availability(screen_df['attributes.name'].tolist())
    logger.debug(f"Available assets: {sum(available_assets)} out of {len(available_assets)}")
    screen_df = screen_df.loc[available_assets]

    portfolio_value = float(portfolio.account.equity)
    logger.debug(f"Portfolio value: {portfolio_value}")
    new_qty = get_optimized_portfolio(screen_df,portfolio_value)

    logger.debug(f"New Quantity of each stock: {new_qty}")
    # cancel all orders existing orders
    logger.debug("Cancelling all existing orders")
    portfolio.cancel_orders([],all_orders=True)
    # get current positions
    current_positions = portfolio.get_positions()
    current_qty = {position.symbol:position.qty for position in current_positions}
    # amount change weight to reach the new weight
    amount_change = {
        symbol:(int(new_qty[symbol]) - int(current_qty.get(symbol,0))) for symbol in new_qty.keys()
    }
    # add stocks that are to be removed from the portfolio
    for symbol in current_qty.keys():
        if symbol not in screen_df['attributes.name'].tolist():
            # now clearing positions to be removed from the portfolio
            logger.debug(f"Removing {symbol} from the portfolio")
            #portfolio.close_positions([symbol])
            #logger.debug(f"Clearing Order submitted for {symbol}")

    logger.debug(f"Amount to change in qty to acheive new Portfolio: {amount_change}")
    # get limit price for each stock
    # logger.debug("Getting limit price for each stock")
    # stock_client = Stock(api_key=settings['ALPACA_API_KEY'],secret_key=settings['ALPACA_SECRET_KEY'], start_date=datetime.now()-timedelta(days=7),timeframe=TimeFrame(4,TimeFrameUnit.Hour))
    symbols = new_qty.keys()
    # data = stock_client.get_data(list(symbols))
    # limit_prices={}
    # for i,j in data.data.items():
    #      #print(i)
    #      limit_prices[i] = get_limit_price(j)
    # submit orders
    for i in range(len(screen_df)):
        symbol = screen_df['attributes.name'].iloc[i]
        # limit_price = round(limit_prices[symbol],2)
        qty = amount_change[symbol]
        if qty == 0:
            logger.debug(f"Qty for {symbol} is 0")
            continue
        if qty < 0:# sell order
            logger.debug(f"Creating sell market order for {symbol} for {abs(qty)}")
            side = OrderSide.SELL
            qty = abs(qty)
            # order = portfolio.create_market_order(symbol,qty,side)
            # logger.debug(f"Order submitted for {symbol}: {order}")
        else:
            logger.debug(f"Creating buy limit order for {symbol} for {qty}")
            side = OrderSide.BUY
            # order = portfolio.create_limit_order(symbol,qty,side,limit_price)
            # order = portfolio.create_market_order(symbol,qty,side)
            # logger.debug(f"Order submitted for {symbol}: {order}")
    

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
    return price_df.iloc[-1]['close']
   

if __name__=="__main__":
    screen_df =screener()
    update_paper_portfolio(screen_df)