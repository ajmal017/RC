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
    orb = 5
    if (120 + orb >= x['SunMoonDegrees']) and (120 - orb <= x['SunMoonDegrees']):
        aspect = 'TR'
    elif (60 + orb >= x['SunMoonDegrees']) and (60 - orb <= x['SunMoonDegrees']):
        aspect = 'SX'
    elif (90 + orb >= x['SunMoonDegrees']) and (90 - orb <= x['SunMoonDegrees']):
        aspect = 'SQ'
    elif (180 + orb >= x['SunMoonDegrees']) and (180 - orb <= x['SunMoonDegrees']):
        aspect = 'OP'
    if (0 + orb >= x['SunMoonDegrees']) and (0 - orb <= x['SunMoonDegrees']):
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
    f, (ax1) = plt.subplots(1, sharex=False, sharey=False)
    x_t = pd.to_datetime(df.index.values)

    ax1.plot(x_t, df['Close'], label='', color='black')
    # ax2.plot(x_t, df['Degrees'], label='', color='blue')
    label_point(df['cob'].astype(str), df['Close'].astype(float), df['Aspect'], ax1)
    plt.show()


def create_df(ticker='S&P500'):
    # ticker = 'NASDAQ_MSFT'

    df_ticker = pd.read_csv('{}{}.csv'.format(cp.dirs['PriceHistories'], ticker, index_col=True))
    df_ticker['Change_pct_' + ticker] = df_ticker['Close_' + ticker].pct_change()
    df_ticker = df_ticker.set_index('Date')

    df_eph = pd.read_csv('Ephemeris2024.csv')
    df_eph['Date'] = pd.to_datetime(df_eph['Date']).dt.strftime('%Y-%m-%d')
    df_eph['SunMoonDegrees'] = df_eph.apply(get_degrees, axis=1)
    df_eph['SunMoonAspect'] = df_eph.apply(get_aspect, axis=1)
    df_eph['SunSign'] = df_eph.apply(get_sign, axis=1)
    df_eph['cob'] = df_eph['Date']
    df_eph = df_eph.set_index('Date')
    # Date,MoonLong,MoonLat,SunLong,SunLat,MercuryLong,MercuryLat,VenusLong,VenusLat,MarsLong,MarsLat,JupiterLong,JupiterLat,SaturnLong,SaturnLat,UranusLong,UranusLat,NeptuneLong,NeptuneLat,PlutoLong,PlutoLat,TrueNodeLong,TrueNodeLat,SouthNodeLong,SouthNodeLat,CupidoLong,CupidoLat,HadesLong,HadesLat,ZeusLong,ZeusLat,KronosLong,KronosLat,ApollonLong,ApollonLat,AdmetosLong,AdmetosLat,VulcanusLong,VulcanusLat,PoseidonLong,PoseidonLat,TransplutoLong,TransplutoLat,BlackMoonLong,BlackMoonLat,CoAscLong,CoAscLat,PolarAscLong,PolarAscLat,DescendantLong,DescendantLat,ImumCoeliLong,ImumCoeliLat,AntiVertexLong,AntiVertexLat,Eq.Dsc.Long,Eq.Dsc.Lat,CoDscLong,CoDscLat,PolarDscLong,PolarDscLat,AriesPntLong,AriesPntLat,LibraPntLong,LibraPntLat,VernalPntLong,VernalPntLat,SelenaLong,SelenaLat,SednaLong,SednaLat,ErisLong,ErisLat
    df_eph = df_eph[['MoonLong', 'SunLong', 'MercuryLong', 'VenusLong', 'MarsLong', 'JupiterLong', 'SaturnLong',
                     'UranusLong', 'NeptuneLong', 'PlutoLong', 'SouthNodeLong', 'SunMoonDegrees', 'SunMoonAspect',
                     'SunSign', 'cob']]

    df_eph = df_eph[(df_eph.index > '2010-01-01') & (df_eph.index < '2018-13-31')]

    # df = df_ticker.join(df_eph, how='inner')
    df = df_eph.join(df_ticker, how='outer')
    df.to_csv('finastro.csv')
    df['Close'] = df['Close_' + ticker]
    # plot_astro_stock(df)
    print(type(df.index))
    df = df[df.index > '2018-11-01']
    print(df.tail)


if __name__ == "__main__":
    # add_detail_to_ephemeris()
    create_df()
    # symbol = '^FTSE'
    # df = create_df(symbol, 60)
    # print(df)
    # df.to_csv('finastro.csv')
    # plot_astro_stock(df) = df_ticker['Date']
