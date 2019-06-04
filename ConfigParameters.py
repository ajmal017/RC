import datetime


#########################################################################################################
# Step 1: Ensure that the below environment directories are valid
#########################################################################################################
dev1 = r'C:/Users/Rushi/Google Drive/Trading/AlgoSys/'
dev2 = r'C:/Users/rushi/Google Drive/Trading/AlgoSys/'
prod = r'C:/Users/Rushi/Dropbox/Production/AlgoSys/'
mac = r'/Users/rushichhapia/Google Drive/MAC/AlgoSys/'
mufg = r'G:/PycharmProjects/PythonWork/AlgoSys/'

#########################################################################################################
# Step 2: Set the environment
#########################################################################################################
environment = dev2
logging = False
#########################################################################################################
# Step 3: No need to change anything below when switching environments. Only change during development.
#########################################################################################################
if environment == mac:
    dirs = {'PriceHistories': r'/Users/rushichhapia/Dropbox/Production/DataHistory/'}
elif environment == mufg:
    dirs = {'PriceHistories': r'G:/PycharmProjects/PythonWork/AlgoSys/DataHistory/'}
else:
    dirs = {'PriceHistories': r'C:/Users/Rushi/Dropbox/Production/DataHistory/'}


files = {
    'TickerExceptions': environment + r'Main/TradeAnalysis - TickerExceptions.csv',
    'TickerMaster': environment + r'Main/TickerMaster.csv',

    'backtest': environment + r'Outputs/backtest.csv',
    'orders': environment + r'Outputs/orders.csv',
    'trades': environment + r'Outputs/trades.csv',
    'metrics': environment + r'Outputs/perf_metrics.csv',
    'pair': environment + r'Outputs/pair.csv',
    'coint_pairs': environment + r'Outputs/coint_pairs.csv',
    'zscores': environment + r'Outputs/zscores.csv',
    'coint_zscores': environment + r'Outputs/coint_zscores.csv',
    'ML': environment + r'Outputs/ML.csv',
    'temp': environment + r'Outputs/_temp.csv',
    'latest_signals': environment + r'Outputs/latest_signals.csv',
    'ib_xml': environment + r'Outputs/IB/ib.xml'
}

quandl_key = 'pn4vPwr_oQm-B9yYoeUB'
# quandl.ApiConfig.api_key = "YOURAPIKEY"
'https://www.quandl.com/api/v3/datatables/SHARADAR/SF1.csv?ticker=AAPL&qopts.columns=ticker,dimension,datekey,revenue&api_key=pn4vPwr_oQm-B9yYoeUB'

equity_price_history_source = 'yahoo'  # yahoo, quandl, google

simulation_lookback = 1500   # number of days
start_trades_date = datetime.datetime.strptime('2012-01-07', '%Y-%m-%d')

# Quandl tickers
fx_tickers = {
    'USD-AUD': 'BOE/XUDLADD',
    'USD-CAD': 'BOE/XUDLCDD',
    'USD-CHF': 'BOE/XUDLSFD',
    'USD-EUR': 'BOE/XUDLERD',
    'USD-GBP': 'BOE/XUDLGBD',
    'USD-JPY': 'BOE/XUDLJYD',
    'USD-NOK': 'BOE/XUDLNKD',
    'USD-NZD': 'BOE/XUDLNDD',
    'USD-SEK': 'BOE/XUDLSKD'
}


crypto_tickers = {
    'BTC-USD': 'BITFINEX/BTCUSD',
    'ETC-USD': 'BITFINEX/ETCUSD',
    'ETH-USD': 'BITFINEX/ETHUSD',
    'LTC-USD': 'BITFINEX/LTCUSD',
    'EOS-USD': 'BITFINEX/EOSUSD',
    'IOT-USD': 'BITFINEX/IOTUSD',
    'XRP-USD': 'BITFINEX/XRPUSD',
    'NEO-USD': 'BITFINEX/NEOUSD',
    'DSH-USD': 'BITFINEX/DSHUSD'
}

ticker_benchmark = 'S&P500'    # S&P500
macro = [
    {'Exchange': 'NYSE', 'Market': 'Main', 'Ticker': 'S&P500', 'Symbol': 'S&P500', 'Name': 'S&P500',
         'Sector': 'Macro', 'Industry Grp': 'Index', 'CCY': 'USD', 'MarketCapBillions': 0.0,
         'YahooTicker': '^GSPC', 'GoogleTicker': 'INDEXCBOE: .INX'},

    {'Exchange': 'CBOE', 'Market': 'Main', 'Ticker': 'CBOE:VIX', 'Symbol': 'VIX', 'Name': 'VIX',
     'Sector': 'Macro', 'Industry Grp': 'Index', 'CCY': 'USD', 'MarketCapBillions': 0.0,
     'YahooTicker': '^VIX', 'GoogleTicker': 'INDEXCBOE: VIX'},

    {'Exchange': 'LON', 'Market': 'MAIN', 'Ticker': 'LON:ISF', 'Symbol': 'ISF', 'Name': 'iShares FTSE100',
         'Sector': 'Macro', 'Industry Grp': 'Index', 'CCY': 'GBP', 'MarketCapBillions': 0.0,
         'YahooTicker': 'ISF.L', 'GoogleTicker': 'LON:ISF'},

    {'Exchange': 'LON', 'Market': 'MAIN', 'Ticker': 'LON:IGUS', 'Symbol': 'IGUS', 'Name': 'iShares S&P500 GBP Hedged',
     'Sector': 'Macro', 'Industry Grp': 'Index', 'CCY': 'GBP', 'MarketCapBillions': 0.0,
     'YahooTicker': 'IGUS.L', 'GoogleTicker': 'LON:IGUS'}


    # PHGP
         ]



lookback = 60
deal_signal_lag = 2 # number of days to wait after signal before executing trade
position_model = 'long_or_short'    # pairs_long_and_short, long_or_short

ewma = {'fast': 50, 'slow': 200}
BollBandFactor = 2.0

rsi_period = 14

maximum_number_of_open_tickers_per_ticker_group = 2
RelativeStrengthPeriods = [5, 20, 60] # 1w (5), 1m (20), 3m (60), 6m (125), 12m (250)

hedge_fx = False

initial_cash = 10000.0
AmountToRiskPerTrade = 500.0
min_pl = 500.0
max_position = 11000.0
min_position = 6000.0




# lse = r'http://www.londonstockexchange.com/statistics/companies-and-issuers/instruments-defined-by-mifir-identifiers-list-on-lse.xlsx'

"""
Problem tickers:
AV.A.L
AV.B.L
PRSM.L
BRD.L
BLU.L
BLUR.L
BME.L
BMR.L
BNN.L
BP.A.L
BP.B.L
BA47.L



"""