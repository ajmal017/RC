import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ConfigParameters as Cp
import xlsxwriter as xls
import Data as Data
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import seaborn as sns
sns.set()


def equity_curve(backtest_file=None, df=None):
    if df is None:
        df = pd.DataFrame.from_csv(backtest_file)  # backtest
    current_date = df.tail(1).index[0]
    x_t = pd.to_datetime(df.index.values)

    f, (ax_eq_ret, ax_drawdown, ax_exposure) = plt.subplots(3, sharex=False, sharey=False)

    # Equity Cumulative Returns: Benchmark1
    cum_return_benchmark1 = df.loc[current_date, 'BarReturnCum_' + Cp.ticker_benchmark] * 100.0
    lbl_benchmark1 = 'Benchmark ({}) = {:3.2f}%'.format(Cp.ticker_benchmark, cum_return_benchmark1)
    ax_eq_ret.plot(x_t, df['BarReturnCum_{}'.format(Cp.ticker_benchmark)], label=lbl_benchmark1, color='black')

    # Equity Cumulative Returns: Strategy
    cum_return_strategy = df.loc[current_date, 'equity_cumulative_returns'] * 100.0
    lbl_strategy = 'Strategy: ' + ' = ' + '{:3.2f}%'.format(cum_return_strategy)
    ax_eq_ret.plot(x_t, df['equity_cumulative_returns'], label=lbl_strategy, color='blue')

    vals = ax_eq_ret.get_yticks()
    ax_eq_ret.set_yticklabels(['{:3.2f}%'.format(pct * 100) for pct in vals])
    ax_eq_ret.set_ylabel('Equity Cumulative Returns')
    ax_eq_ret.legend(loc='best')

    # Drawdown under-water equity curve
    ax_drawdown.plot(x_t, df['Drawdown_pct'], label='Drawdown', color='red')
    vals = ax_drawdown.get_yticks()
    ax_drawdown.set_yticklabels(['{:3.2f}%'.format(pct * 100) for pct in vals])
    ax_drawdown.set_ylabel('Drawdown')

    # Exposures for strategy
    ax_exposure.plot(x_t, df['NetExposure'], label='Net Exposure', color='blue')
    ax_exposure.plot(x_t, df['GrossExposure'], label='Gross Exposure', color='red')
    ax_exposure.set_ylabel('Exposure (GBP)')
    ax_exposure.legend(loc='best')

    plt.show()


def to_excel():
    df = pd.DataFrame.from_csv(Cp.files['backtest'])  # backtest
    df = df[['Cash', 'Equity']]
    # Specify a writer
    writer = pd.ExcelWriter(r'G:\PycharmProjects\PythonWork\AlgoSys\Outputs\AlgoSys.xlsx', engine='xlsxwriter')

    # Write your DataFrame to a file
    df.to_excel(writer, 'Sheet1')

    # Save the result
    writer.save()


def correlation_heatmap():
    # Determine list of tickers with enough history
    df = Data.get_ticker_metadata(exchanges=['NASDAQ', 'NYSE'])
    df = df[df['Sector'] == 'Technology']
    universe_of_tickers = df.index.tolist()
    tickers = Data.get_tickers_with_good_data(universe_of_tickers)

    tickers += list(Cp.crypto_tickers.keys())

    df = Data.create_df_from_tickers(tickers)
    pct_cols = [col for col in df.columns if 'Change_pct_' in col]
    df = df[pct_cols]
    df = df.rename(columns=lambda x: x.replace('Change_pct_', ''))
    df_corr = df.corr()

    for ticker_row, row in df_corr.iterrows():
        for ticker_column in df_corr.columns:
            if ticker_row != ticker_column and abs(row[ticker_column]) > 0.8:
                print('{}_{}: {}'.format(ticker_row, ticker_column, row[ticker_column]))

    data1 = df_corr.values
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)

    ax1.set_xticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1, 1)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # equity_curve(Cp.files['backtest'])
    # to_excel()
    correlation_heatmap()