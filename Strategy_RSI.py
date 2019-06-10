import ConfigParameters as cp


def create_long_short_tickers(tickers, df, ticker_group):
    # Add RSI values
    for ticker in tickers:  # [cp.ticker_benchmark] +
        print(ticker)
        # Calculate the RSI
        delta = df['Close_{}'.format(ticker)].diff()
        up, down = delta.copy(), delta.copy()

        up[up < 0] = 0
        down[down > 0] = 0

        r_up = up.ewm(com=cp.rsi_period - 1, adjust=False).mean()
        r_down = down.ewm(com=cp.rsi_period - 1, adjust=False).mean().abs()

        rsi = 100 - 100 / (1 + r_up / r_down)

        df = df.join(rsi.to_frame('RSI_{}'.format(ticker)))

    # Go Long/Short depending on the ticker_group (exchange-sector)
    if ticker_group in ['NASDAQ_Transportation', 'NASDAQ_Capital Goods', 'NYSE_Finance',
                        'LON_Oil & Gas', 'LON_Utilities', 'LON_Financials']:
        df[ticker_group + '_long_ticker'] = df.apply(low_rsi, axis=1, args=(tickers,))
        df[ticker_group + '_short_ticker'] = df.apply(high_rsi, axis=1, args=(tickers,))
    else:
        df[ticker_group + '_long_ticker'] = df.apply(high_rsi, axis=1, args=(tickers,))
        df[ticker_group + '_short_ticker'] = df.apply(low_rsi, axis=1, args=(tickers,))

    # Add lag to signal
    df[ticker_group + '_long_ticker'] = df[ticker_group + '_long_ticker'].shift(cp.deal_signal_lag, axis=0)
    df[ticker_group + '_short_ticker'] = df[ticker_group + '_short_ticker'].shift(cp.deal_signal_lag, axis=0)

    return df


def low_rsi(x, tickers):
    unsorted_dict = {}

    # Only consider RSIs less than 30
    for ticker in tickers:
        if x['RSI_{}'.format(ticker)] < 30.0:
            unsorted_dict[ticker] = x['RSI_{}'.format(ticker)]

    if len(unsorted_dict) > 0:
        sorted_dict = sorted(unsorted_dict, key=unsorted_dict.get, reverse=True)
        ticker_with_lowest_rsi = sorted_dict[-1]
    else:
        ticker_with_lowest_rsi = ''

    return ticker_with_lowest_rsi


def high_rsi(x, tickers):
    unsorted_dict = {}

    # Only consider RSIs greater than 70
    for ticker in tickers:
        if x['RSI_{}'.format(ticker)] > 70.0:
            unsorted_dict[ticker] = x['RSI_{}'.format(ticker)]

    if len(unsorted_dict) > 0:
        sorted_dict = sorted(unsorted_dict, key=unsorted_dict.get, reverse=True)
        ticker_with_highest_rsi = sorted_dict[0]
    else:
        ticker_with_highest_rsi = ''

    return ticker_with_highest_rsi
