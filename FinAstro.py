import pandas as pd
import ConfigParameters as cp
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sn
import Data as da


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
    df_eph = pd.read_csv('Ephemeris2024.csv')
    df_eph['Date'] = pd.to_datetime(df_eph['Date']).dt.strftime('%Y-%m-%d')
    df_eph['SunMoonActualDegrees'] = df_eph.apply(get_actual_degrees, axis=1)
    df_eph['SunMoonAspectDegrees'] = df_eph.apply(get_degrees, axis=1)
    df_eph['SunMoonAspect'] = df_eph.apply(get_aspect, axis=1)
    df_eph['SunSign'] = df_eph.apply(get_sign, axis=1)
    df_eph['cob'] = df_eph['Date']
    df_eph = df_eph.set_index('Date')
    df_eph = df_eph[['SunLong', 'MoonLong','SunMoonActualDegrees', 'SunMoonAspectDegrees', 'SunMoonAspect',
                     'SunSign', 'cob']]

    return df_eph


def collect_and_prepare_data():
    # Add stock data
    # tickers = ['NASDAQ:MSFT', 'NASDAQ:AAPL']
    tickers = ['LON:IGUS', 'LON:VUKE']
    df_tickers = da.create_df_from_tickers(tickers)
    print(df_tickers.tail(3))
    # Add Ephemeris data
    df_eph = create_ephemeris_df()
    df_eph = df_eph[(df_eph.index > '2010-01-01') & (df_eph.index < '2019-02-28')]
    df = df_eph.join(df_tickers, how='inner')
    df.to_csv('finastro.csv')
    # print(df.tail())
    plot_astro_stock(df)


def machine_learning_process():
    collect_and_prepare_data()


if __name__ == "__main__":
    # add_detail_to_ephemeris()
    machine_learning_process()
    """
    1. Add year
    2. Try to identify whether market is bullish or bearish
    """
