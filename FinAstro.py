import pandas as pd
import pandas_datareader as pdr

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
        sign = 'ARI'
    elif x['SunLong'] >= 30 and x['SunLong'] < 60:
        sign = 'TAU'
    elif x['SunLong'] >= 60 and x['SunLong'] < 90:
        sign = 'GEM'
    elif x['SunLong'] >= 90 and x['SunLong'] < 120:
        sign = 'CAN'
    elif x['SunLong'] >= 120 and x['SunLong'] < 150:
        sign = 'LEO'
    elif x['SunLong'] >= 150 and x['SunLong'] < 180:
        sign = 'VIR'
    elif x['SunLong'] >= 180 and x['SunLong'] < 210:
        sign = 'LIB'
    elif x['SunLong'] >= 210 and x['SunLong'] < 240:
        sign = 'SCO'
    elif x['SunLong'] >= 240 and x['SunLong'] < 270:
        sign = 'SAG'
    elif x['SunLong'] >= 270 and x['SunLong'] < 300:
        sign = 'CAP'
    elif x['SunLong'] >= 300 and x['SunLong'] < 330:
        sign = 'AQU'
    elif x['SunLong'] >= 330 and x['SunLong'] < 360:
        sign = 'PIS'
    return sign


def create_df(ticker, weeks_of_history):
    # df = web.DataReader(ticker, 'yahoo', datetime.today() - timedelta(weeks=weeks_of_history), datetime.today())
    df = pdr.data.get_data_yahoo(ticker)
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
    ax1 = fig.add_subplot(211,  ylabel='Value', axisbg='0.9')    
    df['Close'].plot(ax=ax1, color='y', lw=0.5)
    label_point(df['cob'], df['Close'], df['Aspect'], ax1)
    ax2 = fig.add_subplot(212,  ylabel='Degrees', axisbg='0.9')
    df['Degrees'].plot(ax=ax2, color='b', lw=0.5)            
    plt.show()


if __name__ == "__main__":
    symbol = '^FTSE'
    df = create_df(symbol, 60)
    print(df)
    df.to_csv('finastro.csv')
    plot_astro_stock(df)