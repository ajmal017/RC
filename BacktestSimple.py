import ConfigParameters as Cp
from Order import Order as Order
import pandas as pd


def run(df, portfolio):
    """
    Creates orders from signals and Money & Risk Management
    """
    ticker_groups = portfolio.ticker_group.keys()
    df['Cash'] = 0.0
    df['NetExposure'] = 0.0
    df['GrossExposure'] = 0.0
    df['Equity'] = 0.0

    # Process orders for each day
    for i, curr_row in df.iterrows():
        # Only Manage Orders after the lookback period (typically 180 days)
        if df.index.get_loc(i) > (Cp.lookback * 3):

            # Create, update and cancel orders
            for ticker_group in ticker_groups:
                manage_orders_for_long_only(portfolio, curr_row, ticker_group)

            # Fill open market orders
            execute_orders(portfolio, curr_row)

        # Reset exposures for each bar(day) as they represent the sum of all position values for all tickers.
        # Exposures are not dependent on previous day's exposures
        portfolio.net_exposure = 0.0
        portfolio.gross_exposure = 0.0

        for ticker in portfolio.tickers:
            fx = get_fx(curr_row, ticker)

            position_value = portfolio.position[ticker] * curr_row['Close_' + ticker] * fx
            portfolio.pl[ticker] = position_value - (portfolio.position[ticker] * portfolio.last_deal_price[ticker] * fx)
            df.at[i, 'position_value_' + ticker] = position_value

            portfolio.net_exposure += position_value
            portfolio.gross_exposure += abs(position_value)

        df.at[i, 'Cash'] = portfolio.cash
        df.at[i, 'NetExposure'] = portfolio.net_exposure
        df.at[i, 'GrossExposure'] = portfolio.gross_exposure
        df.at[i, 'Equity'] = portfolio.cash + portfolio.net_exposure

    df['equity_daily_returns'] = df['Equity'].pct_change()
    df['equity_cumulative_returns'] = (df['Equity'] / df['Equity'][0]) - 1.0
    df['BarReturnCum_{}'.format(Cp.ticker_benchmark)] = (df['Close_{}'.format(Cp.ticker_benchmark)] /
                                                         df['Close_{}'.format(Cp.ticker_benchmark)][0]) - 1.0

    # Create Drawdowns
    hwm = [0]
    equity_curve = df['Equity']
    eq_idx = equity_curve.index
    drawdown = pd.Series(index=eq_idx)
    drawdown_pct = pd.Series(index=eq_idx)
    duration = pd.Series(index=eq_idx)

    # Loop over the index range
    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t - 1], equity_curve[t])
        hwm.append(cur_hwm)
        drawdown[t] = equity_curve[t] - hwm[t]
        drawdown_pct[t] = (drawdown[t] / hwm[t])
        duration[t] = 0 if drawdown[t] == 0 else duration[t - 1] + 1
    df['Drawdown'] = drawdown
    df['Drawdown_pct'] = drawdown_pct
    df['DrawdownDuration'] = duration

    # Outputs
    portfolio.df = df
    portfolio.create_orders_and_trades_df()


def manage_orders_for_long_only(portfolio, bar, ticker_group):
    # Get the tickers within the ticker group
    tickers = portfolio.ticker_group[ticker_group]
    max_tickers = 1

    # Determine number of open positions for ticker_group
    open_positions = dict((key, value) for key, value in portfolio.position.items() if key in tickers and value != 0)
    current_open_positions = list(open_positions)

    # Current signals
    long_ticker = bar[ticker_group + '_long_ticker']

    # Case 1: Not enough open positions for tickers in group
    if len(open_positions.keys()) < max_tickers and isinstance(long_ticker, str):

        if long_ticker != '' and long_ticker not in current_open_positions:
            enter_long_position(portfolio, bar, long_ticker)

    # Case 2: If there are more than the maximum #tickers with open positions, then close all positions in ticker group
    elif len(current_open_positions) > max_tickers:
        for open_ticker in current_open_positions:
            exit_position(portfolio, bar, open_ticker)

    # Manage stop orders for current_open_positions
    for open_ticker in current_open_positions:
        manage_stop_orders(portfolio, bar, open_ticker)


def enter_long_position(portfolio, bar, ticker):
    fx = get_fx(bar, ticker)  # fx rate for long ticker
    position = portfolio.cash

    # Determine quantity of assets
    qty = int(position / (bar['EntryPrice_' + ticker] * fx))

    # Determine stop prices
    stop_price = (bar['EntryPrice_' + ticker]) * 0.99

    deal_date = bar['DealDate']
    deal_price = bar['EntryPrice_' + ticker]
    ccy = get_ccy(ticker)

    # Add a Market Order
    market_order = Order(open_date=deal_date, ticker=ticker, quantity=qty, order_type='MKT', price=deal_price,
                         ccy=ccy, fx=fx)

    portfolio.trade_id[ticker] += 1
    market_order.trade_id = portfolio.trade_id[ticker]
    portfolio.orders.append(market_order)

    # Risk Management: Add an associated Stop Order
    stop_order = Order(open_date=deal_date, ticker=ticker, quantity=-qty, order_type='STP', ccy=ccy, fx=fx)
    stop_order.price = stop_price
    stop_order.trade_id = market_order.trade_id
    portfolio.orders.append(stop_order)

    # Hedge FX risk
    manage_fx_hedge(portfolio, bar, market_order)


def exit_position(portfolio, bar, ticker):
    """Creates new MKT orders to flatten current position for a ticker and cancels any associated STP orders"""
    qty = -portfolio.position[ticker]
    deal_date = bar['DealDate']
    deal_price = bar['EntryPrice_' + ticker]

    if qty != 0:
        ccy = get_ccy(ticker)
        fx = get_fx(bar, ticker)

        # Add a Market Order to close current position
        market_order = Order(open_date=deal_date, ticker=ticker, quantity=qty, order_type='MKT', price=deal_price,
                             ccy=ccy, fx=fx)
        market_order.trade_id = portfolio.trade_id[ticker]
        market_order.trade_status = 'CLOSE'
        portfolio.orders.append(market_order)

        # Cancel any OPEN STP orders for the ticker
        for stop_order in portfolio.orders:
            if stop_order.ticker == ticker and stop_order.status == 'OPEN' and stop_order.order_type == 'STP':
                stop_order.cancel_order(deal_date)

        # Remove FX Hedge
        manage_fx_hedge(portfolio, bar, market_order)


def manage_stop_orders(portfolio, bar, ticker):
    """Either adjusts trailing stop or converts STP to MKT order to denote that stop_price has been hit"""
    deal_date = bar['DealDate']
    current_price = bar['EntryPrice_{}'.format(ticker)]
    current_pl = portfolio.pl[ticker]
    min_pl = Cp.min_pl
    position = portfolio.position[ticker]
    ccy = get_ccy(ticker)
    fx = get_fx(bar, ticker)

    for stop_order in portfolio.orders:
        if stop_order.ticker == ticker and stop_order.status == 'OPEN' and stop_order.order_type == 'STP':

            deal_price = portfolio.last_deal_price[ticker]

            # Cancel any OPEN STP orders if there is no position
            if position == 0:
                stop_order.cancel_order(deal_date)

            # Stop Price hit for LONG/SHORT positions, so create a SELL/BUY order to close position
            elif (stop_order.quantity < 0 and current_price < stop_order.price) or \
                    (stop_order.quantity > 0 and current_price > stop_order.price):
                # add a MKT to close position
                market_order = Order(open_date=deal_date, ticker=ticker, quantity=stop_order.quantity,
                                     price=stop_order.price, order_type='MKT', ccy=ccy, fx=fx)

                market_order.trade_status = 'CLOSED'
                market_order.trade_id = stop_order.trade_id
                portfolio.orders.append(market_order)

                # Cancel current STP order
                stop_order.cancel_order(deal_date)

                # Remove FX Hedge
                manage_fx_hedge(portfolio, bar, market_order)

            # Manage Trailing Stop for Long positions with a min_trailing_stop_pct profit
            elif position > 0 and current_pl > min_pl:
                t_stp = (bar['EntryPrice_' + ticker]) * 0.99
                # Only increase the current stop to a higher level
                if t_stp > stop_order.price:
                    new_stop_order = Order(open_date=deal_date, close_date=None, ticker=ticker,
                                                  quantity=stop_order.quantity, order_type='STP', price=t_stp,
                                                  ccy=stop_order.ccy, fx=fx, status='OPEN')

                    new_stop_order.trade_id = stop_order.trade_id
                    portfolio.orders.append(new_stop_order)
                    stop_order.cancel_order(deal_date)


def execute_orders(portfolio, bar):
    """Loop through all OPEN MKT orders to FILL them"""
    for market_order in portfolio.orders:
        if market_order.status == 'OPEN' and market_order.order_type == 'MKT':
            ticker = market_order.ticker
            market_order.close_date = bar['DealDate']

            market_order.fill_order()
            portfolio.position[ticker] += market_order.quantity
            portfolio.last_deal_price[ticker] = market_order.price
            portfolio.cash += market_order.net_consideration

            # Increase the trade_id after
            if portfolio.position[ticker] == 0:
                portfolio.last_deal_price[ticker] = 0.0
                market_order.trade_status = 'CLOSE'


def manage_fx_hedge(portfolio, bar, order):
    if Cp.hedge_fx is True and get_ccy(order.ticker) == 'USD':

        # Case 1: New equity position opened, hedge the USD consideration
        if portfolio.fx_position[order.ticker] == 0.0:
            usd_amount_to_hedge = -1.0 * order.price * order.quantity
            portfolio.fx_position[order.ticker] = usd_amount_to_hedge

            fx_order = Order(open_date=bar['DealDate'], ticker='USD-GBP', quantity=usd_amount_to_hedge, price=order.fx,
                             order_type='MKT', ccy='GBP', fx=1.0, trade_status='OPEN')

        # Case 2: Equity position being closed
        else:
            usd_amount_to_hedge = -1.0 * portfolio.fx_position[order.ticker]
            portfolio.fx_position[order.ticker] = 0.0

            fx_order = Order(open_date=bar['DealDate'], ticker='USD-GBP', quantity=usd_amount_to_hedge, price=order.fx,
                             order_type='MKT', ccy='GBP', fx=1.0, trade_status='CLOSE')

        fx_order.trade_id = '{}_{}'.format(order.trade_id, order.ticker)
        portfolio.orders.append(fx_order)


def get_ccy(ticker):
    ccy = ''
    if 'LON:' in ticker:
        ccy = 'GBX'
    elif '-GBP' in ticker:
        ccy = 'GBP'
    elif 'NYSE:' in ticker or 'NASDAQ:' in ticker:
        ccy = 'USD'
    return ccy


def get_fx(bar, ticker):
    CCYGBP = 1.0   # fx rate against GBP

    if 'LON:' in ticker:
        CCYGBP = bar['Close_GBX-GBP']
    elif '-GBP' in ticker:
        CCYGBP = 1.0
    elif 'NYSE:' in ticker or 'NASDAQ:' in ticker:
        CCYGBP = bar['Close_USD-GBP']
    return CCYGBP
