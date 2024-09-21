import pandas as pd
import backtrader as bt
import qstock as qs
import numpy as np
import os
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import coint
from itertools import combinations
from tqdm import tqdm
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

class FindCointegratedPairs:
    def __init__(self, dataframe, threshold=0.05):
        self.dataframe = dataframe
        self.threshold = threshold

    def check_cointegration(self, array1, array2):
        # Calculate the cointegration between the two series
        _, p_value, _ = coint(array1, array2)
        # Check the cointegration level based on the p-value and threshold
        return p_value < self.threshold

    def check_pair(self, pair):
        idx1, idx2 = pair
        close1 = self.dataframe[idx1].close.array
        close2 = self.dataframe[idx2].close.array
        return (idx1, idx2) if self.check_cointegration(close1, close2) else None

    def find_cointegrated_pairs(self):
        cointegrated_pairs = []
        pairs = list(combinations(range(len(self.dataframe)), 2))
        
        for pair in tqdm(pairs):
            result = self.check_pair(pair)
            if result is not None:
                cointegrated_pairs.append(result)
        
        return cointegrated_pairs


class PairTradingStrategy(BaseStrategy):
    params = dict(
        stake = 100,
        window_size_short = 5,
        window_size_long = 60,
    )

    def __init__(self):
        # stocks selection (data preprocess)
        self.cointegrated_pairs = FindCointegratedPairs(self.datas).find_cointegrated_pairs()
        print("select pairs:", self.cointegrated_pairs)
        # indicators calculation
        self.sma_short = dict()
        self.sma_long = dict()
        self.std_long = dict()
        for pairs in self.cointegrated_pairs:
            raito = self.datas[pairs[0]].close / self.datas[pairs[1]].close
            self.sma_short[pairs] = bt.indicators.SimpleMovingAverage(raito, period=self.params.window_size_short)
            self.sma_long[pairs] = bt.indicators.SimpleMovingAverage(raito, period=self.params.window_size_long)
            self.std_long[pairs] = bt.indicators.StandardDeviation(raito, period=self.params.window_size_long)

    def next(self):
        for pairs in self.cointegrated_pairs:
            z_score = (self.sma_short[pairs][0] - self.sma_long[pairs][0]) / self.std_long[pairs][0]
            if z_score > 1:
                # sell 0 buy 1
                self.log("sell {} and buy {}".format(self.datas[pairs[0]]._name, self.datas[pairs[1]]._name))
                if self.getposition(self.datas[pairs[0]]).size:
                    self.close(data = self.datas[pairs[0]])
                if not self.getposition(self.datas[pairs[1]]).size:
                    self.buy(data = self.datas[pairs[1]], size = self.params.stake)
            elif z_score < -1:
                # buy 0 sell 1
                self.log("sell {} and buy {}".format(self.datas[pairs[1]]._name, self.datas[pairs[0]]._name))
                if not self.getposition(self.datas[pairs[0]]).size:
                    self.buy(data = self.datas[pairs[0]], size = self.params.stake)
                if self.getposition(self.datas[pairs[1]]).size:
                    self.close(data = self.datas[pairs[1]])
            elif abs(z_score) < 0.5:
                # close
                self.log("sell {} and {}".format(self.datas[pairs[0]]._name, self.datas[pairs[1]]._name))
                if self.getposition(self.datas[pairs[0]]).size:
                    self.close(data = self.datas[pairs[0]])
                if self.getposition(self.datas[pairs[1]]).size:
                    self.close(data = self.datas[pairs[1]])
            else:
                # no actions
                pass

def example():
    # Load Data
    hs300_df = qs.index_member('hs300')
    random_stock_codes = hs300_df['股票代码'].sample(n=10, random_state=1).tolist()
    print(random_stock_codes)
    dataframe = qs.get_data(random_stock_codes, \
                            start='20240101', end='20240831', freq='d', fqt=1)
    dataframe.rename(columns={'name': 'code_name'}, inplace=True)
    print(dataframe)

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(PairTradingStrategy)
    # Add the Data Feed to Cerebro
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
    # Plot the back trading process
    cerebro.plot()
    plt.show()

if __name__ == '__main__':
    example()