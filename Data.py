import os
import time
import pandas as pd
import pandas_datareader as pdr
import ConfigParameters as Cp
from datetime import datetime
from pandas.tseries.offsets import BDay
import quandl


def create_df_from_tickers(tickers, start_date=None, end_date=None):
    """
    Create a single DF from a list of tickers, where each column is the Closing price for each ticker
    pct columns will be expressed as decimals e.g. 0.23 is 23%
    """
    # Instantiate the dataframe with a benchmark whose index can be used to outer-join to
    df = pd.read_csv('{}{}.csv'.format(Cp.dirs['PriceHistories'], Cp.ticker_benchmark.replace(':', '_')), index_col=0)
    df['Close_' + Cp.ticker_benchmark].replace(to_replace=0, method='ffill', inplace=True)
    df['Change_pct_' + Cp.ticker_benchmark] = df['Close_' + Cp.ticker_benchmark].pct_change()

    # add FX
    df['Close_GBX-GBP'] = 0.01
    dfa = pd.read_csv('{}{}.csv'.format(Cp.dirs['PriceHistories'], 'USD-GBP'), index_col=0)
    df = df.join(dfa, how='inner')
    df['Change_pct_USD_GBP'] = df['Close_USD-GBP'].pct_change()

    # Create the multi_stock dataframe
    for ticker in tickers + ['CBOE:VIX']:
        dfa = pd.read_csv('{}{}.csv'.format(Cp.dirs['PriceHistories'], ticker.replace(':', '_')), index_col=0)
        df = df.join(dfa, how='inner', rsuffix=ticker)

    for ticker in tickers:
        df['Change_pct_' + ticker] = df['Close_' + ticker].pct_change()
        df['Std_Dev_' + ticker] = df['Close_' + ticker].rolling(window=Cp.lookback).std()
        df['Std_Dev_' + ticker].fillna(method='bfill', inplace=True)
        df['Std_Dev_pct_' + ticker] = df['Std_Dev_' + ticker] / df['Close_' + ticker]
        df['EntryPrice_' + ticker] = 0.5 * (df['Close_' + ticker] + df['Close_' + ticker].shift(1))

    df = df.sort_index(ascending=True)

    # Yahoo data has historical prices until today - 1 business day. This section adds a row to DF for
    # today (cob) so that we can get orders for today
    df.index = pd.to_datetime(df.index)
    last_cob_row = {df.index[-1] + BDay(1): df.iloc[-1]}
    df_last_cob_row = pd.DataFrame.from_dict(last_cob_row, orient='index')
    df = pd.concat([df, df_last_cob_row])

    # Apply simulation date window
    if start_date is not None and end_date is not None:
        s = datetime.strptime(start_date, '%Y-%m-%d')
        e = datetime.strptime(end_date, '%Y-%m-%d')
    elif start_date is not None and end_date is None:
        s = datetime.strptime(start_date, '%Y-%m-%d')
        e = df.tail(1).index[0]
    elif start_date is None and end_date is not None:
        s = df.head(1).index[0]
        e = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        s = df.head(1).index[0]
        e = df.tail(1).index[0]
    df = df[(df.index >= s) & (df.index <= e)]

    # Loop through each column and fill
    for column in df:
        df[column].fillna(method='bfill', inplace=True)
        df[column].fillna(method='ffill', inplace=True)

    df['DealDate'] = df.index
    df['weekday'] = df.index.weekday  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday

    return df


def get_tickers_with_good_data(tickers):
    """
    Good data means enough rows in time series and latest date must be today
    :param tickers:
    :return:
    """
    # Determine most recent date in time series from benchmark
    dfb = pd.read_csv('{}{}.csv'.format(Cp.dirs['PriceHistories'], Cp.ticker_benchmark.replace(':', '_')))

    good_tickers = []
    for ticker in tickers:
        try:
            df = pd.read_csv('{}{}.csv'.format(Cp.dirs['PriceHistories'], ticker.replace(':', '_')))
            df = df.sort_index()
            if len(df.index) < 300:
                if Cp.logging:
                    print('Less than 300 rows: {} ({})'.format(ticker, len(df.index)))
            elif not do_dataframes_have_same_last_n_days_of_histories(df, dfb, 3):
                if Cp.logging:
                    print('Stale ticker: {} ({})'.format(ticker, df.index[-1]))
            else:
                good_tickers.append(ticker)
                if Cp.logging:
                    print('Good ticker: {} ({}) {}'.format(ticker, len(df.index), df.index[-1]))
        except:
            print('No data file: {}'.format(ticker))

    return good_tickers


def do_dataframes_have_same_last_n_days_of_histories(df1, df2, number_of_days=1):
    res = True
    for n in range(number_of_days):
        if df1.index[-n] != df2.index[-n]:
            if Cp.logging:
                print('{} vs {}'.format(df1.index[-n], df2.index[-n]))
            res = False
    return res


# Returns a DF of MetaData for a set of assets based on criteria
def get_ticker_metadata(ticker=None, exchange_sectors=None, exchanges=None, sectors=None, industry_groups=None):
    df = pd.read_csv(Cp.files['TickerMaster'], index_col='Ticker', encoding="ISO-8859-1")
    df['Exchange_Sector'] = df['Exchange'] + '_' + df['Sector']

    if ticker is not None:
        df = df[df.index == ticker]
    elif exchange_sectors is not None:
        df = df[df['Exchange_Sector'].isin(exchange_sectors)]
    elif exchanges is not None:
        df = df[df['Exchange'].isin(exchanges)]
    elif sectors is not None:
        df = df[df['Sector'].isin(sectors)]
    elif industry_groups is not None:
        df = df[df['Industry Grp'].isin(industry_groups)]

    return df


def download_yahoo_eod_data():
    # Obtain a map of stockopedia tickers to Yahoo and IB tickers as they are not the same
    df_tickers = pd.read_csv(Cp.files['TickerMaster'], index_col='Ticker')

    # Remove all csv files from the PriceHistories directory
    file_list = [f for f in os.listdir(Cp.dirs['PriceHistories']) if f.endswith(".csv")]
    for f in file_list:
        os.remove('{}{}'.format(Cp.dirs['PriceHistories'], f))

    for ticker, row in df_tickers.iterrows():

        for download_attempt in range(0, 5):
            time.sleep(3)
            download_success = download_yahoo_eod_data_for_single_ticker(row['YahooTicker'],
                                                                         ticker.replace(':', '_'), ticker)

            if download_success is False:
                print('Retrying {} / {}: {}'.format(ticker, row['YahooTicker'], download_attempt))
                continue
            else:
                # move onto next ticker
                break


def download_yahoo_eod_data_for_single_ticker(yahoo_ticker, filename, close_column_name=''):
    try:
        df = pdr.data.get_data_yahoo(yahoo_ticker)
        df = df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1)
    except:
        print('Problem with Yahoo for ticker {} '.format(yahoo_ticker))
        return False

    try:
        df = df[df['Adj Close'].astype(str) != 'null']
    except:
        pass

    try:
        df['Adj Close'] = df['Adj Close'].astype(float)
        df.rename(columns={'Adj Close': 'Close_' + close_column_name}, inplace=True)
        df.to_csv('{}{}.csv'.format(Cp.dirs['PriceHistories'], filename))
        print('Done: {}'.format(yahoo_ticker))
    except:
        print('Problem with data for ticker:{} '.format(yahoo_ticker))
        return False

    return True


def download_quandl_data():
    quandl.ApiConfig.api_key = Cp.quandl_key

    quandl_tickers = {**Cp.fx_tickers, **Cp.crypto_tickers}

    for ticker, quandl_code in quandl_tickers.items():
        try:
            df = quandl.get([quandl_code], start_date='2010-01-01', collapse='daily', transform='none')
            df.rename(columns={quandl_code + ' - Value': 'Close_{}'.format(ticker)}, inplace=True)
            df.rename(columns={quandl_code + ' - Last': 'Close_{}'.format(ticker)}, inplace=True)

            # BOE data from Quandl data has historical prices until today - 1 business day.
            # Another business day is added in create_df_from_tickers
            if 'BOE' in ticker:
                last_cob_row = {df.index[-1] + BDay(1): df.iloc[-1]}
                df_last_cob_row = pd.DataFrame.from_dict(last_cob_row, orient='index')
                df = pd.concat([df, df_last_cob_row])

            df.to_csv('{}{}.csv'.format(Cp.dirs['PriceHistories'], ticker))
            print('Done: {}'.format(ticker))
        except Exception as e:
            print('Problem with ticker for:{} / {}'.format(ticker, quandl_code))
            print(str(e))


def production():
    download_yahoo_eod_data()
    download_quandl_data()


def static_data():
    # UK Equities
    lse = r'instruments-defined-by-mifir-identifiers-list-on-lse.xlsx'
    df_shares = pd.read_excel(lse, sheet_name='1.1 Shares', header=7)
    df_etfs = pd.read_excel(lse, sheet_name='1.3 ETFs', header=7)
    df_uk = pd.concat([df_shares, df_etfs])

    df_uk.rename(columns={'TIDM': 'Symbol',
                          'Issuer Name': 'Name',
                          'ICB Industry': 'Sector',
                          'ICB Super-Sector Name': 'Industry Grp',
                          'Trading Currency': 'CCY',
                          'LSE Market': 'Market',
                          'MiFIR Identifier Code': 'Type',
                          'Security Mkt Cap (in £m)': 'MarketCap'}, inplace=True)
    df_uk['Exchange'] = 'LON'
    df_uk['YahooTicker'] = df_uk['Symbol'] + '.L'
    df_uk['Ticker'] = df_uk['Exchange'] + ':' + df_uk['Symbol']
    df_uk = df_uk[df_uk['Market'].isin(['MAIN MARKET', 'AIM'])]
    df_uk = df_uk[df_uk['CCY'] == 'GBX']
    df_uk['MarketCapBillions'] = df_uk['MarketCap'] / 1000.0
    df_uk = df_uk[df_uk['MarketCapBillions'] > 1.0]

    # US Stocks
    nsq = r'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download'
    # nsq = r'NASDAQ.csv'
    nyse = r'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download'
    # nyse = r'NYSE.csv'

    df_ndq = pd.read_csv(nsq)
    df_ndq['Exchange'] = 'NASDAQ'
    df_ndq['Ticker'] = df_ndq['Exchange'] + ':' + df_ndq['Symbol']

    df_nyse = pd.read_csv(nyse)
    df_nyse['Exchange'] = 'NYSE'
    df_nyse['Ticker'] = df_nyse['Exchange'] + ':' + df_nyse['Symbol']

    df_us = pd.concat([df_ndq, df_nyse])
    df_us.rename(columns={'Industry': 'Industry Grp'}, inplace=True)
    df_us['MarketCapBillions'] = df_us['MarketCap'] / 1000000000.0
    df_us['Market'] = 'MAIN'
    df_us['CCY'] = 'USD'
    df_us['YahooTicker'] = df_us['Symbol']
    df_us = df_us[df_us['MarketCapBillions'] > 5.0]

    cols = ['Exchange', 'Market', 'Ticker', 'Symbol', 'Name', 'Sector', 'Industry Grp', 'CCY', 'MarketCapBillions',
            'YahooTicker']

    df = pd.concat([df_uk[cols], df_us[cols]])

    df['GoogleTicker'] = df['Ticker'].replace('.', '')

    df = df.append(Cp.macro, ignore_index=True)
    df = df.set_index('Ticker')

    # Apply exceptions
    df_ticker_exceptions = pd.DataFrame.from_csv('{}'.format(Cp.files['TickerExceptions']))
    for ticker, row in df_ticker_exceptions.iterrows():
        df.set_value(ticker, 'YahooTicker', row['YahooTicker'])
        df.set_value(ticker, 'GoogleTicker', row['GoogleTicker'])

    df = df[(df['Sector'] != 'n/a') & (df['Industry Grp'] != 'n/a')]

    df.to_csv('TickerMaster.csv')


def temp_1():
    tickers = ['NYSE:SPY', 'LON:ISF', 'LON:RDSB', 'NASDAQ:MSFT', 'NASDAQ:AAPL', 'NASDAQ:FB', 'NYSE:XOM', 'NYSE:GS',
               'NYSE:JPM', 'NYSE:BA']
    df = create_df_from_tickers(tickers)
    df = df.reset_index()
    df.rename(columns={'index': 'Date'}, inplace=True)
    df.to_csv('stock_prices.csv', index=False)

    print(df.tail())


def temp_2():
    yahoo_ticker = 'MSFT'
    df = pdr.data.get_data_yahoo(yahoo_ticker)
    df = df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1)
    df = df[df['Adj Close'].astype(str) != 'null']
    df['Adj Close'] = df['Adj Close'].astype(float)
    #df.rename(columns={'Adj Close': 'Close_' + yahoo_ticker}, inplace=True)
    df.to_csv('z_{}.csv'.format(yahoo_ticker))
    print('Done: {}'.format(yahoo_ticker))


if __name__ == "__main__":
    print('Start: ', datetime.today())
    production()
    # temp_test()
    # static_data()
    # download_yahoo_eod_data()
    # download_yahoo_eod_data_for_single_ticker(yahoo_ticker='^GSPC', filename=Cp.ticker_benchmark, close_column_name=Cp.ticker_benchmark)
    # download_yahoo_eod_data_for_single_ticker(yahoo_ticker='VUKE.L', filename='LON_VUKE', close_column_name='LON:VUKE')
    # download_yahoo_eod_data_for_single_ticker(yahoo_ticker='MSFT', filename='NYSE_MSFT', close_column_name='NASDAQ:MSFT')
    # download_yahoo_eod_data_for_single_ticker(yahoo_ticker='XLF', filename='NYSE_XLF', close_column_name='NYSE:XLF')
    # temp_2()

    print('Finished: ', datetime.today())
