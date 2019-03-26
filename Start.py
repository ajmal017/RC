import datetime
import ConfigParameters as Cp
import Data as Data
import Strategy as Strategy
from Portfolio import Portfolio as Portfolio
import Performance as Performance
import Graphs as Graphs
import pandas as pd
import Backtest as Backtest


def run_simulation(simulation_name, universe_of_tickers_df, column_to_group_by='Exchange_Sector',
                   generate_outputs=False, run_backtest=True):
    # Get the Universe of tickers as a single DataFrame
    universe_of_tickers = universe_of_tickers_df.index.tolist()

    # Only keep tickers that enough data
    tickers = Data.get_tickers_with_good_data(universe_of_tickers)
    tickers_df = universe_of_tickers_df[universe_of_tickers_df.index.isin(tickers)]

    df = Data.create_df_from_tickers(tickers)
    pd.options.display.float_format = '{:20,.2f}'.format
    ticker_groups = tickers_df[column_to_group_by].unique().tolist()

    # Determine tickers to long and short, by using the strategy to score/rank within ticker_group
    for ticker_group in ticker_groups:
        try:
            # Get all the tickers in the ticker_group, but only keep those with enough price data
            tickers = tickers_df[tickers_df[column_to_group_by] == ticker_group].index.tolist()

            # At least 2 tickers are required for a long-short strategy
            if len(tickers) > 4:
                df = Strategy.create_long_short_tickers(tickers, df, ticker_group, signal_lag=1)
                print('Done: {}'.format(ticker_group))
            else:
                print('Not enough tickers for: ' + ticker_group)
        except:
            print('Failed: {}'.format(ticker_group))

    if run_backtest is True:
        # Initialise Portfolio and run a backtest
        portfolio = Portfolio(df)
        Backtest.run(df, portfolio)
        Performance.metrics(portfolio, simulation_name)

        # Outputs
        if generate_outputs:
            portfolio.orders_df.to_csv(Cp.files['orders'])
            portfolio.trades_df.to_csv(Cp.files['trades'])
            if len(ticker_groups) == 1:
                portfolio.df.to_csv(Cp.files['backtest'])

            portfolio.metrics_df.to_csv(Cp.files['metrics'])
            print(portfolio.metrics_df)
            Graphs.equity_curve(df=portfolio.df)

        return portfolio
    else:
        print('\n\nTrading Day: {}'.format(df.index[-1].strftime('%d-%b-%Y')))
        df = df[-1:].T
        df = df[df.index.str.contains('long_ticker') | df.index.str.contains('short_ticker')]

        df_long_tickers = df[df.index.str.contains('long_ticker')]
        df_long_tickers = df_long_tickers.rename(columns={df_long_tickers.columns[0]: "long"})
        df_long_tickers.index = df_long_tickers.index.str.replace('_long_ticker', '')

        df_short_tickers = df[df.index.str.contains('short_ticker')]
        df_short_tickers = df_short_tickers.rename(columns={df_short_tickers.columns[0]: "short"})
        df_short_tickers.index = df_short_tickers.index.str.replace('_short_ticker', '')

        df = df_long_tickers.join(df_short_tickers)
        print(df)
        df.to_csv(Cp.files['latest_signals'])


def run_simulations_for_each_exchange_sector():
    metrics_for_all_ticker_groups = []

    tickers_df = Data.get_ticker_metadata()
    ticker_groups = tickers_df['Exchange_Sector'].unique().tolist()

    for ticker_group in ticker_groups:
        try:
            p = run_simulation(ticker_group, Data.get_ticker_metadata(exchange_sectors=[ticker_group]))
            metrics_for_all_ticker_groups.append(p.metrics)
        except:
            print('Problem: {}'.format(ticker_group))
            pass
    # All metrics
    df_metrics = pd.DataFrame(metrics_for_all_ticker_groups)
    print(df_metrics.T)
    df_metrics.T.to_csv(Cp.files['metrics'])


def case_sims():
    # Case 1: Run 1 simulation for all tickers. Use this to get EOD orders (metrics + orders/trades)
    df = Data.get_ticker_metadata()
    # run_simulation(simulation_name='All', universe_of_tickers_df=df, generate_outputs=True)

    # Case 2: Run 1 simulation for a specific industry_group or sector (metrics, backtest + orders/trades
    df = df[df['Exchange_Sector'] == 'NASDAQ_Technology']
    run_simulation(simulation_name='Single', universe_of_tickers_df=df, generate_outputs=True)

    # Case 3: Run a simulation to compare the performance metrics for each Exchange_Sector (metrics only)
    # run_simulations_for_each_exchange_sector()


def production():
    df = Data.get_ticker_metadata()
    # Get daily signals
    run_simulation(simulation_name='All', universe_of_tickers_df=df, run_backtest=False)


if __name__ == "__main__":
    print('Start: {}\n'.format(datetime.datetime.today()))
    #production()
    case_sims()
    print('\nFinished: {}'.format(datetime.datetime.today()))


"""
Strategy Implementation:
RS: 1w, 1m and 3m
Entry: long: 3rd highest RSI. The reason for not choosing 1st or 2nd highest RSI is that they are already overbought
Exit1: Loss on current position > £500
Exit2: current long_ticker = short_ticker signal
Exit3: Trailing Stop hit. TP raised for every £500 of profit

"""