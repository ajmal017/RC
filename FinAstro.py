import pandas as pd
import ConfigParameters as cp
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sn


def get_degrees(x):
    degrees = abs(x['SunLong'] - x['MoonLong'])
    if degrees > 180.0:
        degrees = abs(degrees - 360.0)
    return degrees


def get_aspect(x):
    aspect = ''
    orb = 10
    if (120 + orb >= x['Degrees']) and (120 - orb <= x['Degrees']):
        aspect = 'TR'
    elif (60 + orb >= x['Degrees']) and (60 - orb <= x['Degrees']):
        aspect = 'SX'
    elif (90 + orb >= x['Degrees']) and (90 - orb <= x['Degrees']):
        aspect = 'SQ'
    elif (180 + orb >= x['Degrees']) and (180 - orb <= x['Degrees']):
        aspect = 'OP'
    if (0 + orb >= x['Degrees']) and (0 - orb <= x['Degrees']):
        aspect = 'CJ'
    return aspect


def get_sign(x):
    sign=''
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


def create_df_old(ticker, weeks_of_history):
    # df = web.DataReader(ticker, 'yahoo', datetime.today() - timedelta(weeks=weeks_of_history), datetime.today())
    # df = pdr.data.get_data_yahoo(ticker)
    # df_ticker['Date'] = pd.to_datetime(df_ticker['Date']).dt.strftime('%Y-%m-%d')
    df = da.create_df_from_tickers(['S&P500'])
    df_eph = pd.DataFrame.from_csv('Ephemeris2024.csv')
    df['MoonLong'] = df_eph['MoonLong']
    df['SunLong'] = df_eph['SunLong']
    df['Degrees'] = df.apply(get_degrees, axis=1)
    df['Aspect'] = df.apply(get_aspect, axis=1)
    df['Sign'] = df.apply(get_sign, axis=1)
    df['cob'] = df.index
    return df
   

def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x'], point['y'], str(point['val']), fontsize=6)


def plot_astro_stock(df):
    fig = plt.figure()
    #ax1 = fig.add_subplot(2, 1, 1)
    #ax1.plot(df.index, df['Close'], '-', color='b')
    ax1 = fig.add_subplot(211,  ylabel='Value', facecolor='0.9')
    df['Close'].plot(ax=ax1, color='y', lw=0.5)
    label_point(df['cob'].astype(str), df['Close'].astype(float), df['Aspect'], ax1)

    ax2 = fig.add_subplot(212,  ylabel='Degrees', facecolor='0.9')
    df['Degrees'].plot(ax=ax2, color='b', lw=0.5)            
    plt.show()


def add_detail_to_ephemeris():
    df = pd.read_csv('Ephemeris2024.csv')
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    df['Degrees'] = df.apply(get_degrees, axis=1)
    df['Aspect'] = df.apply(get_aspect, axis=1)
    df['Sign'] = df.apply(get_sign, axis=1)
    df['cob'] = df['Date']
    df.to_csv('ephemeris_detail.csv', index=False)


def create_df():
    # ticker = 'NASDAQ_MSFT'
    ticker = 'S&P500'
    df_ticker = pd.read_csv('{}{}.csv'.format(cp.dirs['PriceHistories'], ticker))
    df_ticker['Change_pct_' + ticker] = df_ticker['Close_' + ticker].pct_change()
    df_ticker = df_ticker.set_index('Date')

    df_eph = pd.read_csv('ephemeris_detail.csv')
    df_eph = df_eph.set_index('Date')

    df = df_ticker.join(df_eph, how='inner', on='Date')
    df.to_csv('finastro.csv')
    df['Close'] = df['Close_' + ticker]
    plot_astro_stock(df)

    #print(df.head)


if __name__ == "__main__":
    #add_detail_to_ephemeris()
    create_df()
    # symbol = '^FTSE'
    # df = create_df(symbol, 60)
    # print(df)
    # df.to_csv('finastro.csv')
    # plot_astro_stock(df) = df_ticker['Date']
