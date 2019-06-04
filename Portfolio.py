import ConfigParameters as Cp
import pandas as pd


class Portfolio:
    """Tracks data for each ticker e.g. """

    def __init__(self, df):

        self.ticker_group = {}  # each ticker_group will have a list of tickers which have long/short signals
        self.tickers = []

        # Initialise portfolio metrics
        self.net_exposure = 0.0
        self.gross_exposure = 0.0
        self.cash = Cp.initial_cash
        self.equity = self.cash + self.net_exposure
        self.orders = []
        self.df = df
        self.orders_df = None
        self.trades_df = None
        self.metrics_df = None
        self.metrics = None

        # Identify ticker_groups, which have tickers that have signals
        ticker_groups = [col for col in df.columns if '_long_ticker' in col]
        self.ticker_groups = [tg.replace('_long_ticker', '') for tg in ticker_groups]

        # Determine tickers (which have signals) and the ticker group that they belong to
        for tg in self.ticker_groups:
            tickers_in_group = list(set(df[tg + '_long_ticker'].tolist() + df[tg + '_short_ticker'].tolist()))
            self.ticker_group[tg] = tickers_in_group
            for ticker in tickers_in_group:
                if ticker != '' and str(ticker) != 'nan':
                    self.tickers.append(ticker)

        # Add USD-GBP if FX hedge
        if Cp.hedge_fx is True:
            self.tickers.append('USD-GBP')

        # Initialise metrics for all tickers
        self.position = {key: 0 for key in self.tickers}
        self.fx_position = {key: 0 for key in self.tickers}
        self.pl = {key: 0.0 for key in self.tickers}  # P&L for current open position
        self.trade_id = {key: 0 for key in self.tickers}
        self.fx_trade_id = {key: 0 for key in self.tickers}
        self.last_deal_price = {key: 0.0 for key in self.tickers}

    def create_orders_and_trades_df(self):
        # Create a DataFrame of orders
        list_of_order_dicts = []
        for order in self.orders:
            list_of_order_dicts.append(order.get_dict())
        dfo = pd.DataFrame(list_of_order_dicts)

        dfo = dfo[['open_date', 'trade_id', 'trade_status', 'ticker', 'quantity', 'buy_sell', 'price',
                   'gross_consideration', 'commission', 'fx', 'ccy', 'order_type', 'close_date', 'status']]

        dfo = dfo.sort_values('open_date')
        dfo = dfo.reindex()
        self.orders_df = dfo

        # Create DataFrame of trades
        dfo = dfo[dfo['status'] == 'FILLED']

        df_open = dfo[dfo['trade_status'] == 'OPEN']
        df_close = dfo[dfo['trade_status'] == 'CLOSE']
        df = pd.merge(df_open, df_close, on=['trade_id', 'ticker'], how='outer')

        df.rename(columns={'open_date_x': 'open date', 'close_date_y': 'close date',
                           'quantity_x': 'quantity', 'ccy_x': 'ccy',
                           'price_x': 'price open', 'price_y': 'price close',
                           'fx_x': 'fx open', 'fx_y': 'fx close',
                           'gross_consideration_x': 'gross consideration open', 'commission_x': 'commission open',
                           'gross_consideration_y': 'gross consideration close', 'commission_y': 'commission close'
                           }, inplace=True)

        df['trade net profit'] = df['gross consideration open'] + df['commission open'] + \
                                 df['gross consideration close'] + df['commission close']

        df['holding period days'] = (df['close date'] - df['open date']).astype('timedelta64[D]')

        self.trades_df = df[['open date', 'trade_id', 'ticker', 'ccy', 'quantity', 'price open', 'fx open',
                             'gross consideration open', 'commission open', 'close date', 'price close', 'fx close',
                             'gross consideration close', 'commission close', 'trade net profit',
                             'holding period days']]
