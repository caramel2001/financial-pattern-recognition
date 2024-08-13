import pandas as pd
import numpy as np
from src.pair_trading.copula import ClaytonCopula
from tqdm import tqdm
from statsmodels.tsa.stattools import coint
from itertools import combinations
from itertools import compress
from tqdm import tqdm
import numpy as np
from statsmodels.regression.linear_model import OLS


def find_pairs(data, method="coint"):

    if method == "coint":

        pvalues = []
        pairs = list(combinations(data.columns, 2))

        for x, y in tqdm(pairs, desc="Finding Pairs..."):
            result = coint(data[y], data[x], autolag="bic")
            pvalues.append(result[1])

        pvalues = np.where(np.array(pvalues) < 0.05, True, False)

        return list(compress(pairs, pvalues))


def find_ols_spread(y, x):
    # x = sm.add_constant(x)
    res = OLS(y, x).fit()

    return res.resid


def create_signals(data):

    copula = ClaytonCopula()
    copula.fit(vector=data)
    pdf = copula.pdf(alpha=1, vector=data)
    marginal_u = copula.marginal_cdf(mask=[True, False], vector=data)
    marginal_v = copula.marginal_cdf(mask=[False, True], vector=data)
    marginal_u.index = pd.to_datetime(marginal_u.index)
    marginal_v.index = pd.to_datetime(marginal_v.index)

    # Short Spread Position
    entry_signals_short = np.logical_and(marginal_u < 0.05, marginal_v > 0.95)
    exit_signals_short = np.logical_and(marginal_u >= 0.5, marginal_v <= 0.5)

    # Long Spread Position
    entry_signals_long = np.logical_and(marginal_u > 0.95, marginal_v < 0.05)
    exit_signals_long = np.logical_and(marginal_u <= 0.5, marginal_v >= 0.5)

    return (
        entry_signals_long,
        exit_signals_long,
        entry_signals_short,
        exit_signals_short,
    )


def create_trading_df(df):

    # Returns v - \beta u spread
    # Therefore longing spread is (Low v, High u) and shorting spread is (High v, Low u)
    spread = find_ols_spread(df.iloc[:, 1], df.iloc[:, 0])
    spread.index = pd.to_datetime(spread.index)

    # df should be organised as df[u, v]
    (
        entry_signals_long,
        exit_signals_long,
        entry_signals_short,
        exit_signals_short,
    ) = create_signals(df)
    df_trading_long = pd.concat([spread, entry_signals_long, exit_signals_long], axis=1)
    df_trading_short = pd.concat(
        [-spread, entry_signals_short, exit_signals_short], axis=1
    )

    df_pnl_long = calculate_pnl(df_trading_long)
    df_pnl_short = calculate_pnl(df_trading_short)

    df_pnl_short["Position"] = -df_pnl_short["Position"]
    df_pnl_short["Spread"] = -df_pnl_short["Spread"]

    return df_pnl_long, df_pnl_short


def run_strat(data, pairs):

    runs = {}

    for pair in tqdm(pairs, desc="Running Strat..."):

        df = data[pair]

        df_pnl_long, df_pnl_short = create_trading_df(df)

        runs[str(pair)] = (df_pnl_long, df_pnl_short)

    return runs


def calculate_pnl(df):
    # Initialize variables
    position = 0
    pnl = 0
    trade_price = 0

    # Create a copy of the input DataFrame
    df_out = df.copy()
    df_out[3] = np.zeros(shape=len(df))
    df_out[4] = np.zeros(shape=len(df))
    df_out[5] = np.empty(shape=len(df))
    df_out[6] = np.zeros(shape=len(df))

    # Loop over the DataFrame rows
    for i in range(len(df)):
        # Check if we have a signal to enter a trade
        if df.iloc[i, 1]:
            # If we are not already holding a position, enter a long position
            if position == 0:
                position = 1
                trade_price = df.iloc[i, 0]
        # Check if we have a signal to exit a trade
        elif df.iloc[i, 2]:
            # If we are holding a long position, exit the position
            if position == 1:
                pnl += df.iloc[i, 0] - trade_price
                position = 0
                trade_price = 0

                # Calculate unrealized pnl and add to pnl
        if position == 1:
            unrealized_pnl = (df.iloc[i, 0] - trade_price) * position

        else:
            unrealized_pnl = 0

        # Append the position and pnl to the output DataFrame
        df_out.iloc[i, 3] = position
        df_out.iloc[i, 4] = pnl  # / df_out.iloc[0, 0]
        df_out.iloc[i, 5] = unrealized_pnl  # / df_out.iloc[0, 0]
        df_out.iloc[i, 6] = df_out.iloc[i, 4] + df_out.iloc[i, 5]

    df_out.columns = [
        "Spread",
        "Entry Signal",
        "Exit Signal",
        "Position",
        "Realised PnL",
        "Unrealised PnL",
        "Total PnL",
    ]

    return df_out