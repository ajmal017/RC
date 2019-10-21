import numpy as np
import ConfigParameters as cp


def create_long_short_tickers(tickers, df, ticker_group):

    ticker = tickers[0]

    # Add RSI values
    delta = df['Close_{}'.format(ticker)].diff()
    up, down = delta.copy(), delta.copy()

    up[up < 0] = 0
    down[down > 0] = 0

    r_up = up.ewm(com=cp.rsi_period - 1, adjust=False).mean()
    r_down = down.ewm(com=cp.rsi_period - 1, adjust=False).mean().abs()

    rsi = 100 - 100 / (1 + r_up / r_down)

    df = df.join(rsi.to_frame('RSI_{}'.format(ticker)))

    # SunMoonAspect
    # df[ticker_group + '_long_ticker'] = np.where((df['SunMoonAspect'].isin(['CJ', 'SQ', 'OP'])) | (df['RSI_{}'.format(ticker)] < 30.0), ticker, '')
    aspects = ['CJ', 'SX', 'SQ']
    #df[ticker_group + '_long_ticker'] = np.where((df['SunMoonAspect'].isin(aspects)) & (df['Close_CBOE:VIX'] < 40.0), ticker, '')
    df[ticker_group + '_short_ticker'] = '' # np.where((df['SunMoonAspect'].isin(['OP', 'TR'])) | (df['RSI_{}'.format(ticker)] > 70.0), ticker, '')

    # Don't trade if VIX above 30
    df[ticker_group + '_long_ticker'] = np.where(df['Close_CBOE:VIX'] < 100.0, ticker, '')
    # df[ticker_group + '_long_ticker'] = np.where(df['RSI_{}'.format(ticker)] < 30.0, ticker, '')
    # df[ticker_group + '_short_ticker'] = np.where(df['Close_CBOE:VIX'] < 40.0, ticker, '')
    return df
