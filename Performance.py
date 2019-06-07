import numpy as np
import collections
import pandas as pd
import ConfigParameters as Cp
import statsmodels.api as sm
# np.seterr(invalid='ignore')     # removes RuntimeWarning: invalid value encountered in greater return sum(S > tol)


def metrics(portfolio, simulation_name):
    dfb = portfolio.df
    dft = portfolio.trades_df

    risk_free_rate = 0.0
    pm = collections.OrderedDict()

    pm['simulation_name'] = simulation_name
    pm['Simulation_start_date'] = dfb.head(1).index[0].strftime("%d-%b-%Y")
    pm['Simulation_end_date'] = dfb.tail(1).index[0].strftime("%d-%b-%Y")
    sim_days = (dfb.tail(1).index[0] - dfb.head(1).index[0]).days
    pm['Simulation_duration_days'] = sim_days

    pm['equity_start'] = "{0:,.2f}".format(dfb['Equity'][0])
    pm['equity_end'] = "{0:,.2f}".format(dfb['Equity'][-1])
    pm['total_net_profit'] = "{0:,.2f}".format(dfb['Equity'][-1] - dfb['Equity'][0])

    total_return_factor = dfb['Equity'][-1] / dfb['Equity'][0]
    pm['Total_return'] = "{0:,.2f}%".format(100.0 * (total_return_factor - 1.0))

    average_annual_return_pct = 100.0 * (pow(total_return_factor, (365.0 / sim_days)) - 1)
    pm['Average_Annual_Return'] = "{0:,.2f}%".format(average_annual_return_pct)

    pm['equity_daily_returns_standard_deviation'] = dfb['equity_daily_returns'].std()

    pm['total_number_of_trades'] = "{:,}".format(len(dft.index))
    pm['average_profit_loss_per_trade'] = "{0:,.2f}".format(dft['trade net profit'].mean())
    pm['average_duration_of_trade_days'] = "{0:,.2f}".format(dft['holding period days'].mean())

    pm['total_number_of_winning_trades'] = "{:,}".format(dft[dft['trade net profit'] >= 0.0].count()[0])

    pm['total_number_of_winning_trades_longs'] = "{:,}".format(dft[(dft['trade net profit'] >= 0.0) &
                                                                   (dft['quantity'] > 0)].count()[0])

    pm['total_number_of_winning_trades_shorts'] = "{:,}".format(dft[(dft['trade net profit'] >= 0.0) &
                                                                    (dft['quantity'] < 0)].count()[0])

    pm['net_profit_on_winning_trades'] = "{0:,.2f}".format(dft[dft['trade net profit'] >= 0.0].sum()
                                                           ['trade net profit'])

    pm['average_profit_on_winning_trades'] = "{0:,.2f}".format(dft[dft['trade net profit'] >= 0.0].mean()
                                                               ['trade net profit'])
    pm['average_duration_of_winning_trades_days'] = "{:,.0f}".format(dft[dft['trade net profit'] >= 0.0].mean()
                                                                     ['holding period days'])

    pm['total_number_of_losing_trades'] = "{:,}".format(dft[dft['trade net profit'] < 0.0].count()[0])

    pm['total_number_of_losing_trades_longs'] = "{:,}".format(dft[(dft['trade net profit'] < 0.0) &
                                                                  (dft['quantity'] > 0)].count()[0])

    pm['total_number_of_losing_trades_shorts'] = "{:,}".format(dft[(dft['trade net profit'] < 0.0) &
                                                                   (dft['quantity'] < 0)].count()[0])

    pm['net_profit_on_losing_trades'] = "{0:,.2f}".format(dft[dft['trade net profit'] < 0.0].sum()
                                                          ['trade net profit'])

    pm['average_profit_on_losing_trades'] = "{0:,.2f}".format(dft[dft['trade net profit'] < 0.0].mean()
                                                              ['trade net profit'])
    pm['average_duration_of_losing_trades_days'] = "{:,.0f}".format(dft[dft['trade net profit'] < 0.0].mean()
                                                                    ['holding period days'])

    losing_trades_that_hit_max_stop = dft[dft['trade net profit'] < -abs(Cp.AmountToRiskPerTrade)].count()[0]
    pm['losing_trades_that_hit_max_stop'] = "{:,}".format(losing_trades_that_hit_max_stop)

    win_loss_ratio = abs(dft[dft['trade net profit'] >= 0.0].sum()['trade net profit'] /
                         dft[dft['trade net profit'] < 0.0].sum()['trade net profit'])
    pm['Win/Loss Ratio'] = "{0:,.2f}".format(win_loss_ratio)

    pm['worst_drawdown'] = "{0:,.2f}".format(dfb['Drawdown'].min())
    pm['worst_drawdown_pct'] = "{0:,.2f}%".format(100.0 * dfb['Drawdown_pct'].min())
    pm['longest_drawdown_duration_days'] = "{:,.0f}".format(dfb['DrawdownDuration'].max())

    # sharpe ratio: aim for SR > 1
    sharpe_ratio = np.sqrt(252) * (dfb['equity_daily_returns'].mean() - (risk_free_rate / 252)) / dfb['equity_daily_returns'].std()
    pm['Sharpe_ratio'] = "{0:.2f}".format(sharpe_ratio)

    # Beta and Correlation to FTSE100
    beta, rsquared = calc_stats(dfb, 'equity_daily_returns', 'Change_pct_' + Cp.ticker_benchmark)
    pm['beta_to_benchmark'] = beta
    pm['rsquared_to_benchmark'] = rsquared

    pm['Correlation_to_benchmark'] = dfb['equity_daily_returns'].corr(dfb['Change_pct_' + Cp.ticker_benchmark])

    # Exposure
    pm['max_gross_exposure'] = "{0:,.2f}".format(dfb['GrossExposure'].max())

    # Commission
    pm['total_commission'] = "{0:,.2f}".format(dft['commission open'].sum() + dft['commission close'].sum())

    portfolio.metrics = pm
    portfolio.metrics_df = pd.DataFrame.from_dict(pm, orient='index')
    # print(portfolio.metrics)


def calc_stats(df, y_column, x_column):
    df = df.tail(-(Cp.lookback * 4))    # remove the first 180 days
    df = df.head(-1)                    # remove last line

    y_column = 'Close_NASDAQ:AMAT'
    x_column = 'Close_NASDAQ:MSFT'

    X = sm.add_constant(df[x_column].tolist(), prepend=False)
    y = df[y_column].tolist()
    mod = sm.OLS(endog=y, exog=X, missing='drop', hasconst=True)
    res = mod.fit()
    beta = res.params[1]
    r2 = res.rsquared
    return beta, r2
