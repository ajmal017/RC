class Order:
    order_id = 0

    def __init__(self, open_date=None, close_date=None, ticker=None, quantity=0, order_type='MKT', price=0.0,
                 ccy='GBX', fx=1.0, status='OPEN', trade_status='OPEN'):

        Order.order_id += 1
        self.trade_id = ''                   # 2 FILLED orders with opposite quantity will have same trade_id
        self.status = status                # OPEN, FILLED, CANCELLED
        self.trade_status = trade_status
        self.open_date = open_date          # The date (and time?) the order was OPENED
        self.close_date = close_date        # The date (and time?) the order was CLOSED (i.e. CANCELLED or FILLED)
        self.order_type = order_type        # MKT, STP or LMT
        self.ticker = ticker                # The security being ordered. Use IB Ticker
        self.quantity = quantity            # Total shares ordered. Negative value implies sell/short
        self.buy_sell = 'B' if quantity > 0 else 'S'
        self.price = price                  # Optional limit/stop price. Populate with deal_price when MKT order FILLED
        self.ccy = ccy                      # ccy of security price being traded
        self.fx = fx
        self.gross_consideration = 0.0  #-1.0 * float(self.quantity) * self.price * self.fx
        self.commission = 0.0
        self.net_consideration = 0.0

    def get_dict(self):
        order_dict = {
            'order_id': self.order_id,
            'status': self.status,
            'trade_id': self.trade_id,
            'trade_status': self.trade_status,
            'open_date': self.open_date,
            'close_date': self.close_date,
            'order_type': self.order_type,
            'ticker': self.ticker,
            'quantity': self.quantity,
            'buy_sell': self.buy_sell,
            'price': self.price,
            'fx': self.fx,
            'ccy': self.ccy,
            'gross_consideration': self.gross_consideration,
            'commission': self.commission,
            'net_consideration': self.net_consideration
        }
        return order_dict

    def fill_order(self):
        self.status = 'FILLED'
        self.gross_consideration = -1.0 * float(self.quantity) * self.price * self.fx

        if self.ccy == 'GBX':
            self.commission = -max(abs(self.gross_consideration) * 0.05 / 100.0, 3.0)     # 5bp for UK stocks
        elif self.ccy == 'USD':
            self.commission = -1.0 * self.fx     # $1 for US stocks
        elif self.ccy == 'GBP':
            self.commission = -max(abs(self.gross_consideration) * 0.002 / 100.0, 3.0)

        self.net_consideration = self.gross_consideration + self.commission

    def cancel_order(self, close_date):
        self.close_date = close_date
        self.status = 'CANCELLED'
