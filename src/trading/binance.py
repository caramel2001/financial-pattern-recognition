import ccxt
import pandas as pd
import logging
from datetime import datetime
from src.utils.config import settings

class BinanceTestnetTrader:
    def __init__(self, api_key, secret_key):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'futures'},
        })
        self.exchange.set_sandbox_mode(True)
        logging.basicConfig(filename='trading_log.log', level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def place_order(self, symbol, side, amount, price=None, order_type='market', tp=None, sl=None):
        try:
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'amount': amount,
                'price': price if order_type == 'limit' else None,
            }
            order = self.exchange.create_order(**order_params)
            logging.info(f"Order placed: {order}")

            if tp or sl:
                self.set_stop_loss_take_profit(symbol, side, amount, tp, sl)

            return order
        except Exception as e:
            logging.error(f"Failed to place order: {e}")
            return None

    def set_stop_loss_take_profit(self, symbol, side, amount, tp=None, sl=None):
        try:
            if tp:
                self.exchange.create_order(
                    symbol=symbol,
                    side='sell' if side == 'buy' else 'buy',
                    type='limit',
                    price=tp,
                    quantity=amount
                )
                logging.info(f"Take profit set at {tp}")

            if sl:
                self.exchange.create_order(
                    symbol=symbol,
                    side='sell' if side == 'buy' else 'buy',
                    type='stop_market',
                    stopPrice=sl,
                    quantity=amount
                )
                logging.info(f"Stop loss set at {sl}")
        except Exception as e:
            logging.error(f"Failed to set TP/SL: {e}")

    def get_trades(self, symbol):
        try:
            trades = self.exchange.fetch_my_trades(symbol)
            trades_df = pd.DataFrame(trades)
            logging.info(f"Fetched trades for {symbol}")
            return trades_df
        except Exception as e:
            logging.error(f"Failed to fetch trades: {e}")
            return pd.DataFrame()

    def calculate_pnl(self, trades_df):
        if trades_df.empty:
            logging.info("No trades found for PnL calculation.")
            return None

        trades_df['cost'] = trades_df['cost'].astype(float)
        trades_df['profit'] = trades_df['amount'].astype(float) * trades_df['price'].astype(float)
        trades_df['PnL'] = trades_df.apply(lambda row: row['profit'] - row['cost'] if row['side'] == 'buy' else row['cost'] - row['profit'], axis=1)

        total_pnl = trades_df['PnL'].sum()
        logging.info(f"Total PnL calculated: {total_pnl}")
        return trades_df, total_pnl

    def test_connection(self):
        try:
            balance = self.exchange.fetch_balance()
            logging.info("Connection successful")
            return balance
        except Exception as e:
            logging.error(f"Connection test failed: {e}")

# Example usage
print(settings['BINANCE_TESTNET_API_KEY'],settings['BINANCE_TESTNET_SECRET_KEY'])
trader = BinanceTestnetTrader(settings['BINANCE_TESTNET_API_KEY'], settings['BINANCE_TESTNET_SECRET_KEY'])
trader.test_connection()
trader.place_order('BTC/USDT', 'buy', 0.01, tp=30000, sl=28000)
trades = trader.get_trades('BTC/USDT')
# pnl_report, total_pnl = trader.calculate_pnl(trades)
print(trades)
