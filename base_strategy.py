import backtrader as bt

class BaseStrategy(bt.Strategy):
    """
    This is a base strategy. Each ``strategy`` class will inherit from here.
    """

    params = (
        ('log_enabled', False),
    )

    def log(self, txt):
        """ Logging function for this strategy. """
        dt = self.datetime.date()
        print(f"{dt}, {txt}")

    def notify_order(self, order):
        """ Triggered upon changes to orders. """

        # Print out the date, security name, order number and status.
        if self.params.log_enabled:
            dt, dn = self.datetime.date(), order.data._name
            type = "Buy" if order.isbuy() else "Sell"
            self.log(
                f"[Order Notify]\t"
                f"Order {order.ref:3d},\tType {type},\tStatus {order.getstatusname()} \t"
                f"Size: {order.created.size:9.4f}, Price: {order.created.price:9.4f}, "
            )

        # Suppress notification if it is just a submitted order.
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Check if an order has been completed
        if order.status in [order.Completed] and self.params.log_enabled:
            self.log(
                f"[Order Completed]\t"
                f"{'BUY' if order.isbuy() else 'SELL'} EXECUTED for {dn}, "
                f"Price: {order.executed.price:6.2f}, "
                f"Cost: {order.executed.value:6.2f}, "
                f"Comm: {order.executed.comm:4.2f}, "
                f"Size: {order.created.size:9.4f}, "
            )

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        """Provides notification of closed trades."""
        if trade.isclosed and self.params.log_enabled:
            self.log(
                f"[Close Trade]\t"
                "{} Closed: PnL Gross {}, Net {},".format(
                    trade.data._name, round(trade.pnl, 2), round(trade.pnlcomm, 1),
                )
            )

    def print_signal(self, dataline):
        """ Print out OHLCV. """
        if self.params.log_enabled:
            self.log(
                "o {:5.2f}\th {:5.2f}\tl {:5.2f}\tc {:5.2f}\tv {:5.0f}".format(
                    self.datas[dataline].open[0],
                    self.datas[dataline].high[0],
                    self.datas[dataline].low[0],
                    self.datas[dataline].close[0],
                    self.datas[dataline].volume[0],
                )
            )

    def print_dev(self):
        """ For development logging. """
        if not self.params.log_enabled:
            return
        
        self.log(
            f"Value: {self.broker.cash:5.2f}, "
            f"Cash: {self.broker.get_value():5.2f}, "
            f"Close:{self.datas[1].close[0]:5.2f}, "
        )

    def print_status(self):
        """Print current status."""
        if not self.params.log_enabled:
            return
        
        cash = self.broker.cash
        total_value = self.broker.get_value()
        self.log(f"[Current Status]\tCash: {cash:5.2f}, Total Value: {total_value:5.2f}")
        for i, data in enumerate(self.datas):
            position = self.broker.getposition(data)
            if not position.size:
                continue
            self.log(
                f"[Current Status]\t"
                f"Data {i} ({data._name}): "
                f"Position Size: {position.size:5.2f}, "
                f"Price: {position.price:5.2f}"
            )