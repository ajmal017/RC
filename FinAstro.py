from pandas.tseries.offsets import BDay
import datetime
import matplotlib.pyplot as plt
import Data as da
import pandas as pd
import numpy as np
import ConfigParameters as cp
import Strategy_FinAstro as Strategy
from Portfolio import Portfolio as Portfolio
import Performance as Performance
import Graphs as Graphs
import Backtest as Backtest
import seaborn as sns
sns.set()


def get_actual_degrees(x):
    return abs(x['SunLong'] - x['MoonLong'])


def get_degrees(x):
    degrees = abs(x['SunLong'] - x['MoonLong'])
    if degrees > 180.0:
        degrees = abs(degrees - 360.0)
    return degrees


def get_aspect(x):
    aspect = ''
    orb = 5
    if (120 + orb >= x['SunMoonAspectDegrees']) and (120 - orb <= x['SunMoonAspectDegrees']):
        aspect = 'TR'
    elif (60 + orb >= x['SunMoonAspectDegrees']) and (60 - orb <= x['SunMoonAspectDegrees']):
        aspect = 'SX'
    elif (90 + orb >= x['SunMoonAspectDegrees']) and (90 - orb <= x['SunMoonAspectDegrees']):
        aspect = 'SQ'
    elif (180 + orb >= x['SunMoonAspectDegrees']) and (180 - orb <= x['SunMoonAspectDegrees']):
        aspect = 'OP'
    if (0 + orb >= x['SunMoonAspectDegrees']) and (0 - orb <= x['SunMoonAspectDegrees']):
        aspect = 'CJ'
    return aspect


def get_sign(x):
    sign = ''
    if x['SunLong'] >= 0 and x['SunLong'] < 30:
        sign = '01_ARI'
    elif x['SunLong'] >= 30 and x['SunLong'] < 60:
        sign = '02_TAU'
    elif x['SunLong'] >= 60 and x['SunLong'] < 90:
        sign = '03_GEM'
    elif x['SunLong'] >= 90 and x['SunLong'] < 120:
        sign = '04_CAN'
    elif x['SunLong'] >= 120 and x['SunLong'] < 150:
        sign = '05_LEO'
    elif x['SunLong'] >= 150 and x['SunLong'] < 180:
        sign = '06_VIR'
    elif x['SunLong'] >= 180 and x['SunLong'] < 210:
        sign = '07_LIB'
    elif x['SunLong'] >= 210 and x['SunLong'] < 240:
        sign = '08_SCO'
    elif x['SunLong'] >= 240 and x['SunLong'] < 270:
        sign = '09_SAG'
    elif x['SunLong'] >= 270 and x['SunLong'] < 300:
        sign = '10_CAP'
    elif x['SunLong'] >= 300 and x['SunLong'] < 330:
        sign = '11_AQU'
    elif x['SunLong'] >= 330 and x['SunLong'] < 360:
        sign = '12_PIS'
    return sign


def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        aspect = str(point['val'])
        if aspect == 'nan':
            aspect = ''
        ax.text(point['x'], point['y'], aspect, fontsize=6)


def plot_astro_stock(df):
    # fig = plt.figure()
    f, (ax1, ax2) = plt.subplots(2, sharex=False, sharey=False)
    x_t = pd.to_datetime(df.index.values)

    ax1.plot(x_t, df['Change_pct_S&P500'], label='', color='black')
    ax2.plot(x_t, df['SunMoonActualDegrees'], label='', color='blue')
    label_point(df['cob'].astype(str), df['Change_pct_S&P500'].astype(float), df['SunMoonAspect'], ax1)
    plt.show()


def create_ephemeris_df():
    df = pd.read_csv('Ephemeris2024.csv')
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    df['SunMoonActualDegrees'] = df.apply(get_actual_degrees, axis=1)
    df['SunMoonAspectDegrees'] = df.apply(get_degrees, axis=1)
    df['SunMoonAspectRaw'] = df.apply(get_aspect, axis=1)
    df['SunSign'] = df.apply(get_sign, axis=1)
    df['cob'] = df['Date']
    # print(df_eph[['Date', 'cob']].dtypes)
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df['day_of_week'] = df.index.weekday  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday
    df['previous_day'] = df['day_of_week'].shift(1)
    df['next_day'] = df['day_of_week'].shift(-1)

    # If there is no aspect on Friday, then use Saturday's aspect
    df['SunMoonAspectRawNext'] = df['SunMoonAspectRaw'].shift(-1)
    df['SunMoonAspect'] = np.where((df['day_of_week'] == 4.0) & (df['SunMoonAspectRaw'] == ''), df['SunMoonAspectRawNext'], df['SunMoonAspectRaw'])

    # If there is no aspect on Monday, then use Sunday's aspect
    df['SunMoonAspectRawPrevious'] = df['SunMoonAspectRaw'].shift(1)
    df['SunMoonAspect'] = np.where((df['day_of_week'] == 0.0) & (df['SunMoonAspectRaw'] == ''), df['SunMoonAspectRawPrevious'], df['SunMoonAspectRaw'])

    df = df[['SunLong', 'MoonLong','SunMoonActualDegrees', 'SunMoonAspectDegrees', 'SunSign', 'cob', 'SunMoonAspect',
             'day_of_week', 'previous_day','SunMoonAspectRawPrevious', 'next_day', 'SunMoonAspectRawNext',
             'SunMoonAspectRaw']]
    df.to_csv(cp.files['ephemeris'])
    return df


def collect_and_prepare_data():
    # Add stock data
    # tickers = ['NASDAQ:MSFT', 'NASDAQ:AAPL']
    tickers = ['LON:FTSE100']
    df_tickers = da.create_df_from_tickers(tickers)

    # Add Ephemeris data
    df_eph = create_ephemeris_df()
    df_eph = df_eph[(df_eph.index > '2001-01-01') & (df_eph.index < '2019-08-28')]
    df = df_eph.join(df_tickers, how='inner')

    cols = ['year', 'weekday',
            'SunLong',
            'MoonLong',
            'SunMoonActualDegrees',
            'SunMoonAspectDegrees',
            'SunMoonAspect',
            'SunSign',
            'Close_S&P500',
            'Change_pct_S&P500',
            'Close_CBOE:VIX',
            'Close_USD-GBP',
            'Change_pct_USD_GBP',
            'Close_LON:FTSE100',
            'Change_pct_LON:FTSE100',
            'Std_Dev_LON:FTSE100',
            'Std_Dev_pct_LON:FTSE100'
            ]
    df[cols].to_csv('finastro.csv')

    #plot_astro_stock(df)


def finastro_sim():
    # Add stock data
    ticker_group = 'FinAstro'
    tickers = ['LON:FTSE100']
    df_tickers = da.create_df_from_tickers(tickers)

    # Add Ephemeris data
    df_eph = create_ephemeris_df()
    df_eph = df_eph[(df_eph.index > '2001-01-01') & (df_eph.index < '2019-09-30')]
    df = df_eph.join(df_tickers, how='inner')

    # Generate long/short tickers i.e. signals
    df = Strategy.create_long_short_tickers(tickers, df, ticker_group)

    # Run backtest
    portfolio = Portfolio(df)
    Backtest.run(df, portfolio)
    Performance.metrics(portfolio, ticker_group)

    # Outputs
    pd.options.display.float_format = '{:20,.2f}'.format
    portfolio.orders_df.to_csv(cp.files['orders'])
    portfolio.trades_df.to_csv(cp.files['trades'])
    portfolio.df.to_csv(cp.files['backtest'])

    portfolio.metrics_df.to_csv(cp.files['metrics'])
    print(portfolio.metrics_df)
    Graphs.equity_curve(df=portfolio.df)


if __name__ == "__main__":
    print('Start: {}\n'.format(datetime.datetime.today()))
    finastro_sim()
    # collect_and_prepare_data()
    # create_ephemeris_df()
    print('\nFinished: {}'.format(datetime.datetime.today()))

"""
1. Add year
2. Try to identify whether market is bullish or bearish
"""
