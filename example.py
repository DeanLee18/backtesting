import pandas as pd
import backtrader as bt
import qstock as qs
from base_strategy import BaseStrategy
from add_data import add_data
from set_broker import set_broker
from add_analyzer import add_analyzer

'''
--------------------------------------------- [Notes] ---------------------------------------------
self.datas is backtrader.feeds.PandasData type.

It has 7 keys:
'datetime', 'open', 'high', 'low', 'close', 'volume', 'openinterest'
(openinterest can not be read by qstock.get_data, so its values are all nan.)

The structure of self.datas is like this:
self.datas[0] -> all data of first stock (from start date to end date)
self.datas[-1].open -> all open price of last stock (from start date to end date)
self.datas[0].close[0] -> the close price of the first stock on today
self.datas[0].close[-1] -> the close price of the first stock on yesterday
self.datas[0].datetime.date(0) -> to get the datetime of today
self.datas[0].datetime.date(-1) -> to get the datetime of yesterday

Similarly, if you want to use some indicators, you can calculate before backtesting and its structure can be the same.
----------------------------------------------------------------------------------------------------
'''

class SmaStrategy(BaseStrategy):
    params = dict(
        period = 30,
        stake = 100,
    )
    def __init__(self):
        self.inds = list()
        for i, data in enumerate(self.datas):
            self.inds.append(bt.indicators.SimpleMovingAverage(data.close, period=self.params.period))
            # If you want to use other indicators, you can search in https://www.backtrader.com/docu/indautoref/

    def next(self):
        self.print_status()
        for i, data in enumerate(self.datas):
            position = self.getposition(data)
            if not position.size:
                if data.close[0] > self.inds[i][0]:
                    self.buy(data = data, size = self.params.stake)  
            elif data.close[0] < self.inds[i][0]:
                self.sell(data = data, size = self.params.stake)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(SmaStrategy)

    # Add the Data Feed to Cerebro
    stock_list = ['中国平安', '海科新源', '德尔股份', '南都电源', '科恒股份']
    dataframe = qs.get_data(stock_list, start='20240101',end='20240831')
    # dataframe = pd.read_csv("data/sh600000_history_k_data.csv", parse_dates=['date'])
    # dataframe.loc[dataframe.sample(frac=0.5).index, 'code'] = '000000'
    add_data(dataframe, cerebro)

    # Set the broker
    set_broker(cerebro)

    # Set analyzers
    add_analyzer(cerebro)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    result = cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    print(
            f"AnnualReturn: {result[0].analyzers._AnnualReturn.get_analysis()}, \n"
            f"DrawDown: {result[0].analyzers._DrawDown.get_analysis()}, \n"
            f"Returns: {result[0].analyzers._Returns.get_analysis()}, \n"
            f"SharpeRatio: {result[0].analyzers._SharpeRatio.get_analysis()}, \n"
            # f"GrossLeverage: {result[0].analyzers._GrossLeverage.get_analysis()}, \n"
            # f"TimeReturn: {result[0].analyzers._TimeReturn.get_analysis()}"
    )
