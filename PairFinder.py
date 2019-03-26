import statsmodels.tsa.stattools as ts
import pandas as pd
import datetime
import ConfigParameters as Cp
import Data as Data
import itertools
import Performance as Pf
import numpy as np
from sklearn import linear_model
import statsmodels.api as sm


def is_pair_cointegrated_(df, ticker1, ticker2):

    is_cointegrated = False
    df = df.tail(Cp.lookback * 100)

    df = df.rename(columns={'Close_{}'.format(ticker2): 's_close'})     # strong (y)
    df = df.rename(columns={'Close_{}'.format(ticker1): 'w_close'})     # weak (x)

    # First check if cointegrated over long time period
    beta_hr, alpha, r2 = Pf.calc_stats(df, 's_close', 'w_close')
    df['residuals'] = df['s_close'] - (beta_hr * df['w_close'])

    ts_res = ts.adfuller(df['residuals'])
    critical_values = ts_res[4]

    # if test statistic is less than 10% level, then co-integrated at that confidence level
    if ts_res[0] < critical_values['10%'] and 0.7 < beta_hr < 1.3:
        is_cointegrated = True

    return is_cointegrated, beta_hr, df['residuals']


def is_pair_cointegrated(df, ticker1, ticker2):

    df['log_price_x'] = np.log(df['Close_{}'.format(ticker1)])
    df['log_price_y'] = np.log(df['Close_{}'.format(ticker2)])

    x = df['log_price_x']
    y = df['log_price_y']

    pair_is_cointegrated = False
    regr = linear_model.LinearRegression()
    x_constant = pd.concat([x, pd.Series([1] * len(x), index=x.index)], axis=1)
    regr.fit(x_constant, y)
    beta = regr.coef_[0]
    alpha = regr.intercept_
    spread = y - (x * beta) - alpha
    df['spread'] = spread

    # Now perform ADF test
    adf = sm.tsa.stattools.adfuller(spread, maxlag=1)
    test_statistic = adf[0]
    critical_values = adf[4]

    if test_statistic < critical_values['10%']:
        pair_is_cointegrated = True

    return pair_is_cointegrated, beta, df['spread']


def find_cointegrated_pairs_by_exchange_sector(start_date='2006-01-01'):

    cointegrated_pairs = []

    universe_of_tickers_df = Data.get_ticker_metadata()
    exchange_sectors = universe_of_tickers_df['Exchange_Sector'].unique().tolist()
    try:
        exchange_sectors.remove('NYSE_Macro')
    except:
        pass

    for exchange_sector in exchange_sectors:
        df_tm = universe_of_tickers_df[universe_of_tickers_df['Exchange_Sector'] == exchange_sector]
        tickers = df_tm.index.tolist()
        print(exchange_sector)
        for ticker_pair in list(itertools.combinations(tickers, 2)):

            try:
                df = Data.create_df_from_tickers(list(ticker_pair), start_date=start_date)
                is_coint, hr, spreads = is_pair_cointegrated(df, ticker_pair[0], ticker_pair[1])

                if is_coint:
                    cointegrated_pairs.append(ticker_pair)
                    print('{} Good'.format(ticker_pair))
                else:
                    print(ticker_pair)
            except:
                print('Problem with: {}'.format(ticker_pair))

    with open(Cp.files['coint_pairs'], 'w') as f:
        for pair in cointegrated_pairs:
            f.write('{}_{}\n'.format(pair[0], pair[1]))


def create_zscores_for_pairs_in_same_exchange_sector():
    list_of_pairs = []

    universe_of_tickers_df = Data.get_ticker_metadata()
    universe_of_tickers_df = universe_of_tickers_df[universe_of_tickers_df['Sector'] != 'Macro']
    ticker_groups = universe_of_tickers_df['Exchange_Sector'].unique().tolist()

    for ticker_group in ticker_groups:
        print(ticker_group)
        df_tm = universe_of_tickers_df[universe_of_tickers_df['Exchange_Sector'] == ticker_group]
        tickers = df_tm.index.tolist()

        for ticker_pair in list(itertools.combinations(tickers, 2)):
            pair = {}
            try:
                df = Data.create_df_from_tickers(list(ticker_pair))

                df['ratio'] = df['Close_' + ticker_pair[0]] / df['Close_' + ticker_pair[1]]
                df['ratio_mean'] = df['ratio'].rolling(window=Cp.lookback).mean()
                df['ratio_std_dev'] = df['ratio'].rolling(window=Cp.lookback).std()
                df['zscore'] = (df['ratio'] - df['ratio_mean']) / df['ratio_std_dev']
                pair['Exchange_Sector'] = ticker_group
                pair['ticker_pair'] = ticker_pair[0] + '_' + ticker_pair[1]
                pair['ratio'] = df['ratio'][-1]
                pair['ratio_mean'] = df['ratio_mean'][-1]
                pair['ratio_std_dev'] = df['ratio_std_dev'][-1]
                pair['zscore'] = df['zscore'][-1]
                print(pair)
                list_of_pairs.append(pair)
            except:
                print('Problem: {}'.format(ticker_pair))
                pass

    df = pd.DataFrame(list_of_pairs)
    df.set_index('ticker_pair', inplace=True)
    df.to_csv(Cp.files['zscores'])


def cointegrated_zscores():
    df = pd.read_csv(Cp.files['zscores'])
    df = df[['ticker_pair', 'Exchange_Sector', 'ratio', 'ratio_mean', 'ratio_std_dev', 'zscore']]

    with open(Cp.files['coint_pairs']) as f:
        list_of_coint_pairs = f.read().splitlines()

    # Only get zscore rows for cointegrated pairs
    df = df[df['ticker_pair'].isin(list_of_coint_pairs)]

    # Get individual tickers
    df['Ticker1'], df['Ticker2'] = df['ticker_pair'].str.split('_', 1).str

    df = df.set_index('ticker_pair')
    df.to_csv(Cp.files['coint_zscores'])



if __name__ == '__main__':
    print('Start: ', datetime.datetime.today())
    #temp()
    find_cointegrated_pairs_by_exchange_sector()
    #create_zscores_for_pairs_in_same_exchange_sector()
    #cointegrated_zscores()
    print('Finished: ', datetime.datetime.today())
