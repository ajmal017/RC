import pandas as pd
import Data as Data
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import ConfigParameters as Cp
import Performance as Pf
import PairFinder as Pa
import seaborn as sn
sn.set()


def analyse(ticker1, ticker2):
    df = Data.create_df_from_tickers(tickers=[ticker1, ticker2], start_date='2008-01-01')

    # Compute bollinger bands
    df['ratio'] = df['Close_' + ticker2] / df['Close_' + ticker1]
    df['ratio_mean'] = df['ratio'].rolling(window=Cp.lookback).mean()
    df['ratio_std'] = df['ratio'].rolling(window=Cp.lookback).std()
    df['std_upper'] = df['ratio_mean'] + df['ratio_std'] * 3.0
    df['std_lower'] = df['ratio_mean'] - df['ratio_std'] * 3.0

    # Is ratio cointegrated?
    is_coint, beta, df['spreads'] = Pa.is_pair_cointegrated(df, ticker1, ticker2)
    print('Cointegrated: {}, Beta: {}'.format(is_coint, beta))

    # Create plots
    current_date = df.tail(1).index[0]
    # x_t = pd.to_datetime(df.index.values)
    x_t = df.index.values
    f, (ax_ratio, ax_spreads, ax1, ax2) = plt.subplots(4, sharex=False, sharey=False)

    ratio = df.loc[current_date, 'ratio']
    lbl = 'Ratio: ' + ' = ' + '{:3.4f}'.format(ratio)
    ax_ratio.plot(x_t, df['ratio'], label=lbl, color='black')

    ratio_mean = df.loc[current_date, 'ratio_mean']
    lbl = 'Ratio Mean: ' + ' = ' + '{:3.4f}'.format(ratio_mean)
    ax_ratio.plot(x_t, df['ratio_mean'], label=lbl, color='grey')

    std_upper = df.loc[current_date, 'std_upper']
    lbl = 'Boll. Upper: ' + ' = ' + '{:3.4f}'.format(std_upper)
    ax_ratio.plot(x_t, df['std_upper'], label=lbl, color='blue')

    std_lower = df.loc[current_date, 'std_lower']
    lbl = 'Boll. Lower: ' + ' = ' + '{:3.4f}'.format(std_lower)
    ax_ratio.plot(x_t, df['std_lower'], label=lbl, color='red')
    ax_ratio.legend(loc='best')

    # spreads
    latest_spread = df.loc[current_date, 'spreads']
    lbl = 'spread: ' + ' = ' + '{:3.4f}'.format(latest_spread)
    ax_spreads.plot(x_t, df['spreads'], label=lbl, color='blue')
    ax_spreads.legend(loc='best')

    # ticker 1
    latest_price_ticker1 = df.loc[current_date, 'Close_' + ticker1]
    lbl = ticker1 + ': ' + ' = ' + '{:3.4f}'.format(latest_price_ticker1)
    ax1.plot(x_t, df['Close_' + ticker1], label=lbl, color='blue')
    ax1.legend(loc='best')

    # ticker 2
    latest_price_ticker2 = df.loc[current_date, 'Close_' + ticker2]
    lbl = ticker2 + ': ' + ' = ' + '{:3.4f}'.format(latest_price_ticker2)
    ax2.plot(x_t, df['Close_' + ticker2], label=lbl, color='blue')
    ax2.legend(loc='best')

    df.to_csv(Cp.files['pair'])

    plt.show()


def rolling_stats(df, y_column, x_column, window=20):
    #     dataframe to hold the results
    res = pd.DataFrame(index=df.index)

    for i in range(0,len(df.index)):

        if len(df) - i >= window:
            # break the df into smaller chunks
            chunk = df.iloc[i:window+i,:]
            # calc_stats is a function created from the code above,
            # refer to the Gist at the end of the article.
            beta,alpha,r2 = Pf.calc_stats(chunk, y_column, x_column)
            res.set_value(chunk.tail(1).index[0],"beta",beta)
            res.set_value(chunk.tail(1).index[0],"alpha",alpha)
            res.set_value(chunk.tail(1).index[0],"r2",r2)
            # print "%s beta: %.4f \t alpha: %.4f" % (chunk.tail(1).index[0],b,a)
    res = res.dropna()
    return res


if __name__ == "__main__":
    ticker_pair = 'NASDAQ:FB_NASDAQ:MSFT'
    # ticker_pair = 'NYSE:TD_NYSE:BLK'
    # ticker_pair = 'LON:IGUS_LON:VUSA'
    # ticker_pair = 'NASDAQ:AABA_NYSE:VMW'
    # ticker_pair = 'LON:ISF_LON:MIDD'
    tickers = ticker_pair.split('_')
    analyse(tickers[0], tickers[1])
