# Day Trading Volatility Breakouts Systematically 
# This code is part of a project that implements a volatility breakout strategy for day trading.
# The system employs a straightforward volatility breakout strategy. The specific rules for this model are as follows:

# Calculate Daily ATR: Compute the Average True Range (ATR) with a period of 5 days.
# Determine Volatility Breakout Bands:
# Long Entry: Opening price + 0.4 * ATR(5)
# Short Entry: Opening price - 0.4 * ATR(5)
# Set Stop-Loss: For each trade, set a stop-loss at 0.4 * ATR(5). Exit the trade if the market retraces to the opening price after breaching the breakout level.
# Trade Frequency: In each market, execute only one long breakout attempt and one short breakout attempt per day.
# Risk Management: Allocate a small portion of the account to each trade. The backtest uses 0.33% of the account per trade. Consequently, in a single market, you can enter up to two trades per day (one long and one short), risking a maximum of 0.66% of the account.
# Exit Strategy: Exit either at the stop-loss or at the end of the trading day. The stop-loss remains fixed at the entry point (the opening price) throughout the day.

import pandas as pd
from backtesting import Strategy
import pandas_ta as ta

class VolatilityBreakout(Strategy):
    """
    A simple volatility breakout strategy for day trading.
    """
    atr_period = 5  # ATR period
    def init(self):
        # Calculate the 5-day ATR
        self.data['ATR'] = ta.atr(self.data['High'], self.data['Low'], self.data['Close'], length=self.atr_period)
        self.atr = self.I(self._calculate_atr, self.data, self.atr_period)

    def next(self):
        # Get the current opening price and ATR
        open_price = self.data.Open[-1]
        atr_value = self.atr[-1]
        # Calculate the breakout levels
        long_entry = open_price + 0.4 * atr_value
        short_entry = open_price - 0.4 * atr_value
        # Check for long entry condition
        if self.data.Close[-1] > long_entry:
            self.buy(sl=open_price - 0.4 * atr_value)
        # Check for short entry condition
        elif self.data.Close[-1] < short_entry:
            self.sell(sl=open_price + 0.4 * atr_value)
        # Exit at the end of the day, convert the datetime index to UTC NYSE time
        timestamp = self.data.index[-1]
        # check the tzinfo of the last timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize('America/New_York')
        else:
            timestamp = timestamp.tz_convert('America/New_York')
        if timestamp.hour == 15 and timestamp.minute == 59:
            # Close all positions at the end of the day
            if self.position.is_long:
                self.position.close()
            elif self.position.is_short:
                self.position.close()

    @staticmethod
    def _calculate_atr(data, period):
        return ta.atr(data['High'], data['Low'], data['Close'], length=period)
    
