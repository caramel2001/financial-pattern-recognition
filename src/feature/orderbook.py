from enum import Enum
import time
from datetime import datetime
from typing import Dict, List
import logging
from tabulate import tabulate
import asyncio

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ccxt
from ccxt import Exchange
from ccxt.binance import binance
from ccxt.coinbaseadvanced import coinbaseadvanced
from ccxt.bybit import bybit
from src.utils.config import settings
from loguru import logger

class CryptoOrderbook:
    def __init__(self):
        self.ts_delta_observation_ms_threshold = 2000

    def get_coinbase_exchange(self):
        return coinbaseadvanced({
           'defaultType' : "swap",
           'apiKey' : settings["COINBASE_API_KEY"],
           'secret' : settings["COINBASE_SECRET_KEY"]
        })

    # def collect_order_book(self, exchange_names: List[Exchange], symbol:str, depth: int = 10000):
    #     param= {
    #         "limit" : depth,
    #         "symbol": symbol,
    #     }
    #     orderbooks = asyncio.gather(*[self._fetch_orderbook(symbol,exchange,param) for exchange in exchange_names])
    #     return orderbooks

    def _fetch_orderbook(self,symbol : str, exchange : Exchange, fetch_ob_params : Dict):
        try:
            print(fetch_ob_params)
            ob = exchange.fetch_order_book(symbol=symbol, params=fetch_ob_params)
            is_valid = True
            if 'timestamp' in ob and ob['timestamp']:
                update_ts_ms = ob['timestamp']
                ts_delta_observation_ms = int(datetime.now().timestamp()*1000) - update_ts_ms
                logger.info(f"ts_delta_observation_ms: {ts_delta_observation_ms}")
                is_valid = True if ts_delta_observation_ms<=self.ts_delta_observation_ms_threshold else False

            bid_prices = [ x[0] for x in ob['bids'] ]
            ask_prices = [ x[0] for x in ob['asks'] ]
            min_bid_price = min(bid_prices)
            max_bid_price = max(bid_prices)
            min_ask_price = min(ask_prices)
            max_ask_price = max(ask_prices)

            mid = (max([ x[0] for x in ob['bids'] ]) + min([ x[0] for x in ob['asks'] ])) / 2

            logger.info(f"{exchange.name} {symbol} mid: {mid}, min_bid_price: {min_bid_price}, max_bid_price: {max_bid_price}, min_ask_price: {min_ask_price}, max_ask_price: {max_ask_price}, range: {max_ask_price-min_bid_price}")


            return {
                        'source' : exchange.name,
                        'orderbook' : ob,
                        'mid' : mid,
                        'min_bid_price' : min_bid_price,
                        'max_bid_price' : max_bid_price,
                        'min_ask_price' : min_ask_price,
                        'max_ask_price' : max_ask_price,
                        'is_valid' : is_valid
                    }
        except Exception as fetch_err:
            logger.info(f"_fetch_orderbook failed for {exchange.name}: {fetch_err}")
            return {
                'source' : exchange.name,
                'is_valid' : False
            }

    def post_process_orderbook(self, orderbooks: List[Dict],price_level_increment: float = 1):
        df_imbalances = pd.DataFrame(columns=['timestamp_ms', 'mid', 'imbalance', 'total_amount', 'pct_imbalance'])
        valid_orderbooks = [ ob for ob in orderbooks if ob['is_valid']]
        max_min_bid_price = max([ ob['min_bid_price'] for ob in valid_orderbooks if ob])
        best_bid_price = max([ob['max_bid_price'] for ob in valid_orderbooks if ob])
        min_max_ask_price = min([ob['max_ask_price'] for ob in valid_orderbooks if ob])
        best_ask_price = min([ob['min_ask_price'] for ob in valid_orderbooks if ob])

        logger.info(f"max_min_bid_price: {max_min_bid_price}, min_max_ask_price: {min_max_ask_price}, best_bid_price: {best_bid_price}, best_ask_price: {best_ask_price}.")

        aggregated_orderbooks = {
            'bids' : {},
            'asks' : {}
        }

        mid = [ x['mid'] for x in valid_orderbooks][0] # use Bybit as mid reference
        def round_to_nearest(price, increment):
            return round(price / increment) * increment
        for orderbook in valid_orderbooks:
            bids = orderbook['orderbook']['bids']
            asks = orderbook['orderbook']['asks']

            for bid in bids:
                price = round_to_nearest(bid[0], price_level_increment)
                amount = bid[1]
                if bid[0] > max_min_bid_price:
                    existing_amount = 0
                    if price in aggregated_orderbooks['bids']:
                        existing_amount = aggregated_orderbooks['bids'][price]['amount']
                    amount_in_base_ccy = existing_amount + amount
                    amount_in_usdt = amount_in_base_ccy * mid
                    aggregated_orderbooks['bids'][price] = {
                        'price' : price,
                        'amount' : amount_in_base_ccy,
                        'amount_usdt' : amount_in_usdt
                    }

            for ask in asks:
                price = round_to_nearest(ask[0], price_level_increment)
                amount = ask[1]
                if ask[0] < min_max_ask_price:
                    existing_amount = 0
                    if price in aggregated_orderbooks['asks']:
                        existing_amount = aggregated_orderbooks['asks'][price]['amount']
                    amount_in_base_ccy = existing_amount + amount
                    amount_in_usdt = amount_in_base_ccy * mid
                    aggregated_orderbooks['asks'][price] = {
                        'price' : price,
                        'amount' : amount_in_base_ccy,
                        'amount_usdt' : amount_in_usdt
                    }

        sorted_asks = dict(sorted(aggregated_orderbooks['asks'].items(), key=lambda item: item[0], reverse=True))
        sorted_bids = dict(sorted(aggregated_orderbooks['bids'].items(), key=lambda item: item[0], reverse=True))

        pd_aggregated_orderbooks_asks = pd.DataFrame(sorted_asks)
        pd_aggregated_orderbooks_bids = pd.DataFrame(sorted_bids)
    
        pd_aggregated_orderbooks_asks = pd_aggregated_orderbooks_asks.transpose()
        pd_aggregated_orderbooks_bids = pd_aggregated_orderbooks_bids.transpose()

        sum_asks_amount_usdt = pd.to_numeric(pd_aggregated_orderbooks_asks['amount_usdt']).sum()
        sum_bids_amount_usdt = pd.to_numeric(pd_aggregated_orderbooks_bids['amount_usdt']).sum()

        ask_resistance_price_level = pd_aggregated_orderbooks_asks['amount_usdt'].idxmax()
        bid_support_price_level = pd_aggregated_orderbooks_bids['amount_usdt'].idxmax()

        pd_aggregated_orderbooks_asks['is_max_amount_usdt'] = pd_aggregated_orderbooks_asks.index == ask_resistance_price_level
        pd_aggregated_orderbooks_bids['is_max_amount_usdt'] = pd_aggregated_orderbooks_bids.index == bid_support_price_level

        pd_aggregated_orderbooks_asks['str_amount_usdt'] = pd_aggregated_orderbooks_asks['amount_usdt'].apply(lambda x: f'{x:,.2f}')
        pd_aggregated_orderbooks_bids['str_amount_usdt'] = pd_aggregated_orderbooks_bids['amount_usdt'].apply(lambda x: f'{x:,.2f}')

        pd_aggregated_orderbooks_asks_ = pd_aggregated_orderbooks_asks[['price', 'amount', 'str_amount_usdt', 'is_max_amount_usdt']]
        pd_aggregated_orderbooks_asks_.rename(columns={'str_amount_usdt': 'amount_usdt'}, inplace=True)
        pd_aggregated_orderbooks_bids_ = pd_aggregated_orderbooks_bids[['price', 'amount', 'str_amount_usdt', 'is_max_amount_usdt']]
        pd_aggregated_orderbooks_bids_.rename(columns={'str_amount_usdt': 'amount_usdt'}, inplace=True)


        spread_bps = (best_ask_price-best_bid_price) / mid * 10000
        spread_bps = round(spread_bps, 0)
        logger.info(f"mid: {mid}, spread_bps between bests: {spread_bps} (If < 0, arb opportunity). Range {max_min_bid_price} - {min_max_ask_price} (${int(min_max_ask_price-max_min_bid_price)})")

        logger.info(f"asks USD {sum_asks_amount_usdt:,.2f}, best: {best_ask_price:,.2f}")
        # logger.info(f"{tabulate(pd_aggregated_orderbooks_asks_.reset_index(drop=True), headers='keys', tablefmt='psql', colalign=('right', 'right', 'right'), showindex=False)}")

        logger.info(f"bids USD {sum_bids_amount_usdt:,.2f}, best: {best_bid_price:,.2f}")
        # logger.info(f"{tabulate(pd_aggregated_orderbooks_bids_.reset_index(drop=True), headers='keys', tablefmt='psql', colalign=('right', 'right', 'right'), showindex=False)}")

        # compile a dictionary of orderbook stats that can used to decide on making trades
        data_dict={
            'spread' : best_ask_price - best_bid_price,
            'spread_bps' : spread_bps,
            'max_min_bid_price' : max_min_bid_price,
            'min_max_ask_price' : min_max_ask_price,
            'best_ask_price' : best_ask_price,
            'best_bid_price' : best_bid_price,
            'sum_asks_amount_usdt' : sum_asks_amount_usdt,
            'sum_bids_amount_usdt' : sum_bids_amount_usdt
        }
        return pd_aggregated_orderbooks_asks, pd_aggregated_orderbooks_bids,data_dict

    def plot_orderbook(self, pd_aggregated_orderbooks_asks:pd.DataFrame,pd_aggregated_orderbooks_bids:pd.DataFrame,nrows=20):
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        pd_aggregated_orderbooks_asks = pd_aggregated_orderbooks_asks.tail(nrows)
        pd_aggregated_orderbooks_bids = pd_aggregated_orderbooks_bids.head(nrows)


        sns.barplot(
            x=-pd_aggregated_orderbooks_asks['amount_usdt'],
            y=pd_aggregated_orderbooks_asks['price'],
            color='red',
            orient='h',
            ax=ax1,
            label='Asks'
        )

        sns.barplot(
            x=pd_aggregated_orderbooks_bids['amount_usdt'],
            y=pd_aggregated_orderbooks_bids['price'],
            color='lime',
            orient='h',
            ax=ax2,
            label='Bids'
        )


        ax1.set_title('Order Book Volume Profile - Asks', color='white')
        ax2.set_title('Order Book Volume Profile - Bids', color='white')

        ax1.set_xlabel('')
        ax2.set_xlabel('Volume (USD)', color='white')
        ax1.set_ylabel('Price (USD)', color='white')
        ax2.set_ylabel('Price (USD)', color='white')

        ax1.tick_params(colors='white')
        ax2.tick_params(colors='white')

        ax1.invert_yaxis()
        ax2.invert_yaxis()

        legend1 = ax1.legend()
        legend2 = ax2.legend()

        for text in legend1.get_texts():
            text.set_color('white')
        for text in legend2.get_texts():
            text.set_color('white')
        plt.tight_layout()

        plt.show()

        return fig

if __name__ == '__main__':
    client = CryptoOrderbook()
    # Define necessary parameters
    coinbase_symbol = "SOL-PERP-INTX"
    depth = 10000
    param = {
        "limit": depth,
        "symbol": coinbase_symbol,
    }
    exchange = coinbaseadvanced({
        'defaultType' : "swap",
    })
    coinbase_orderbooks = client._fetch_orderbook(symbol=coinbase_symbol, exchange=exchange,fetch_ob_params=param)
    # getting binance orderbooks
    binance_symbol = "SOLUSDT"
    depth = 10000
    param = {
        "limit": depth,
        "symbol": binance_symbol,
    }
    binance = binance({
        'defaultType' : "swap",
    })
    binance_orderbooks = client._fetch_orderbook(symbol=binance_symbol, exchange=binance,fetch_ob_params=param)
    bybit_symbol = "SOLUSDT"
    depth = 10000
    param = {
        "limit": depth,
        "symbol": bybit_symbol,
    }
    bybit = bybit({
        'defaultType' : "swap",
    })
    bybit_orderbooks = client._fetch_orderbook(symbol=bybit_symbol, exchange=bybit,fetch_ob_params=param)
    # Process the order books
    pd_aggregated_orderbooks_asks, pd_aggregated_orderbooks_bids,orderbook_features = client.post_process_orderbook([coinbase_orderbooks,binance_orderbooks], price_level_increment=1)
    print(orderbook_features)
    # Plot the order imbalance
    client.plot_orderbook(pd_aggregated_orderbooks_asks, pd_aggregated_orderbooks_bids,nrows = 40)

    
