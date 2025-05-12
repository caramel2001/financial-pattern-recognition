from src.utils.config import settings
from src.feature.orderbook import CryptoOrderbook
from src.data_client.crypto import CoinbaseCrypto
import talib as ta
from datetime import datetime,timedelta
import pandas as pd
import mplfinance as mpf
from ccxt.coinbaseadvanced import coinbaseadvanced


def get_orderbook_data(self,price_level_increment=0.5):
    client = CryptoOrderbook()
    # Define necessary parameters
    symbol = self.symbol
    depth = 10000
    param = {
        "limit": depth,
        "symbol": symbol,
    }
    exchange = coinbaseadvanced({
        'defaultType' : "swap",
    })
    orderbooks = client._fetch_orderbook(symbol=symbol, exchange=exchange,fetch_ob_params=param)
    # Process the order books
    pd_aggregated_orderbooks_asks, pd_aggregated_orderbooks_bids,orderbook_features = client.post_process_orderbook([orderbooks], price_level_increment=price_level_increment)

    # get plot 
    return pd_aggregated_orderbooks_asks, pd_aggregated_orderbooks_bids,orderbook_features