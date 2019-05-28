import datetime
import Data as Data
import ConfigParameters as Cp
import numpy as np
import pandas as pd


def create_long_short_tickers(tickers, df, ticker_group, signal_lag):
    return rsi(tickers, df, ticker_group, signal_lag)
    # return momentum_relative_strength(tickers, df, ticker_group, signal_lag)


def rsi(tickers, df, ticker_group, signal_lag):

    # Add Relative strength values
    for ticker in [Cp.ticker_benchmark] + tickers:
        df['score_' + ticker] = 0.0

        # Calculate the RSI
        delta = df['Close_{}'.format(ticker)].diff()
        up, down = delta.copy(), delta.copy()

        up[up < 0] = 0
        down[down > 0] = 0

        rUp = up.ewm(com=Cp.rsi_period - 1, adjust=False).mean()
        rDown = down.ewm(com=Cp.rsi_period - 1, adjust=False).mean().abs()

        rsi = 100 - 100 / (1 + rUp / rDown)

        df = df.join(rsi.to_frame('RSI_{}'.format(ticker)))
        # df['score_' + ticker] = np.where((df['RSI_{}'.format(ticker)] > 30.0) & (df['RSI_{}'.format(ticker)] < 70.0), 0.0, df['RSI_{}'.format(ticker)])
        df['score_' + ticker] = df['RSI_{}'.format(ticker)]

        # df['score_' + ticker] = df['score_' + ticker] * (-1.0)  # short if above 70, so shorts get lower score i.e. -70

        # Go long 2nd highest, and short the 2nd lowest score
        df = rank_ticker_scores(tickers, df, ticker_group, 1, len(tickers)-1)

        # Add lag to signal
        df[ticker_group + '_long_ticker'] = df[ticker_group + '_long_ticker'].shift(signal_lag, axis=0)
        df[ticker_group + '_short_ticker'] = df[ticker_group + '_short_ticker'].shift(signal_lag, axis=0)
        df[ticker_group + '_score'].shift(signal_lag)

        df[ticker_group + '_long_ticker'] = df[ticker_group + '_long_ticker'].replace(np.nan, '', regex=True)
        df[ticker_group + '_short_ticker'] = df[ticker_group + '_short_ticker'].replace(np.nan, '', regex=True)
        df['score_' + ticker] = df['score_' + ticker].replace(np.nan, 0.0, regex=True)

        return df


def momentum_relative_strength(tickers, df, ticker_group, signal_lag):
    """
    Relative Strength (RS) is a metric that show how well a stock has performed compared to its benchmark
    The idea behind this strategy is to go long tickers with high RS and short tickers with low RS.

    Current Rules:
    Entry:

    :param tickers:
    :param df: A DataFrame created
    :param ticker_group: ticker group
    :return: a DataFrame with long/short tickers for each day
    """
    # Add Relative strength values
    for ticker in [Cp.ticker_benchmark] + tickers:

        df['score_' + ticker] = 0.0

        # Calculate the RS for each lookback period and ticker combination
        for lookback in Cp.RelativeStrengthPeriods:

            # Calculate % change between price now and lookback date
            df['strategy_Change_pct_{}_{}_days'.format(ticker, lookback)] = \
                df['Close_{}'.format(ticker)] / df['Close_{}'.format(ticker)].shift(lookback)

            if ticker != Cp.ticker_benchmark:
                df['strategy_RS_{}_{}_days'.format(ticker, lookback)] = \
                    (df['strategy_Change_pct_{}_{}_days'.format(ticker, lookback)] /
                     df['strategy_Change_pct_{}_{}_days'.format(Cp.ticker_benchmark, lookback)]) - 1

                # Dividing by lookback gives more weight to the more recent RS values
                # But, by not dividing by lookback, all RS periods are given equal weight as we want consistency
                df['score_' + ticker] += df['strategy_RS_{}_{}_days'.format(ticker, lookback)] # / lookback

    # Go long 2nd highest, and short the 2nd lowest score
    df = rank_ticker_scores(tickers, df, ticker_group, 2, len(tickers)-1)

    # score has to be positive to remain long
    # This makes system worse!
    # df[ticker_group + '_short_ticker'] = df.apply(filter_short_tickers, axis=1, args=(ticker_group + '_long_ticker', ticker_group + '_short_ticker',))
    # df[ticker_group + '_long_ticker'] = df.apply(filter_long_tickers, axis=1, args=(ticker_group + '_long_ticker',))

    # Add lag to signal
    df[ticker_group + '_long_ticker'] = df[ticker_group + '_long_ticker'].shift(signal_lag, axis=0)
    df[ticker_group + '_short_ticker'] = df[ticker_group + '_short_ticker'].shift(signal_lag, axis=0)
    df[ticker_group + '_score'].shift(signal_lag)

    df[ticker_group + '_long_ticker'] = df[ticker_group + '_long_ticker'].replace(np.nan, '', regex=True)
    df[ticker_group + '_short_ticker'] = df[ticker_group + '_short_ticker'].replace(np.nan, '', regex=True)
    df['score_' + ticker] = df['score_' + ticker].replace(np.nan, 0.0, regex=True)

    return df


def rank_ticker_scores(tickers, df, ticker_group, long_rank, short_rank):
    """
    :param tickers:
    :param df:
    :param ticker_group:
    :param long_rank:
    :param short_rank:
    :return: df
    """
    list_of_score_columns = ['score_' + s for s in tickers]

    # Identify score columns with highest and 2nd highest value for each row
    # Long ticker has rank of _long_ticker and _short_ticker has rank of short)rank
    df[ticker_group + '_long_ticker'] = df.apply(nth_largest_ticker, axis=1, args=(list_of_score_columns, long_rank,))
    df[ticker_group + '_short_ticker'] = df.apply(nth_largest_ticker, axis=1, args=(list_of_score_columns, short_rank,))

    df[ticker_group + '_score'] = df.apply(ticker_group_score, axis=1, args=(ticker_group + '_long_ticker',
                                                                             ticker_group + '_short_ticker',))
    return df


def filter_long_tickers(x, long_ticker_col):
    long_ticker = x[long_ticker_col]

    if 0.0 < x['score_' + long_ticker] < 0.2:
        long_ticker = ''

    return long_ticker


def filter_short_tickers(x, long_ticker_col, short_ticker_col):
    long_ticker = x[long_ticker_col]
    short_ticker = x[short_ticker_col]

    if x['score_' + long_ticker] < 0.0:
        short_ticker = long_ticker

    return short_ticker


def nth_largest_ticker(x, ticker_score_columns, rank):
    unsorted_dict = {}
    # create a dict of ticker: score
    for ticker_score_column in ticker_score_columns:
        unsorted_dict[ticker_score_column] = x[ticker_score_column]

    # sort the dict in descending order
    sorted_dict = sorted(unsorted_dict, key=unsorted_dict.get, reverse=True)
    return sorted_dict[rank-1].replace('score_', '')


def ticker_group_score(x, col1, col2):
    return abs(x['score_' + x[col1]] - x['score_' + x[col2]])
