import numpy as np
import pandas as pd
import qstock as qs
import backtrader as bt

# Create a Stratey
class TestStrategy(bt.Strategy):
    def next(self):
        for data in self.datas:
            print(f"{data.datetime.date(0)}: Close data for {data._name}: {data.close[0]}")

def add_data(dataframe, cerebro):
    """
    处理股票数据并加载到 cerebro 中，不修改 cerebro 的其他部分
    :param dataframe: 从 qs.get_data 获取的股票数据
    :param cerebro: 初始化好的 cerebro 实例
    """
    if 'date' in dataframe:
        dataframe.set_index('date', inplace=True)
    if 'datetime' in dataframe:
        dataframe.set_index('datetime', inplace=True)
    # 创建一个空的数据框用于对齐数据
    aligned_data = pd.DataFrame(index=dataframe.index.unique())
    processed_data = {}

    # 处理每一个股票代码的数据
    for code in dataframe['code'].unique():
        stock_data = dataframe.query(f"code == '{code}'")
        stock_data_aligned = pd.merge(aligned_data, stock_data, left_index=True, right_index=True, how='left')

        # 对齐数据框并填补缺失值
        stock_data_aligned = pd.merge(aligned_data, stock_data, left_index=True, right_index=True, how='left')
        stock_data_aligned[['volume']] = stock_data_aligned[['volume']].fillna(0)
        stock_data_aligned[['code', 'open', 'high', 'low', 'close']] = \
            stock_data_aligned[['code', 'open', 'high', 'low', 'close']].fillna(method='pad')
        if 'code_name' in stock_data_aligned:
            stock_data_aligned[['code_name']] = stock_data_aligned[['code_name']].fillna(method='pad')
            processed_data[stock_data_aligned[['code_name']][0]] = stock_data_aligned
        else:
            processed_data[code] = stock_data_aligned

    # 将处理后的数据加载到 cerebro 中
    for name, data in processed_data.items():
        datafeed = bt.feeds.PandasData(dataname=data)  # 转换为 backtrader 的 PandasData
        cerebro.adddata(datafeed, name=str(name))  # 加载到 cerebro 实例中

if __name__ == '__main__':
    dataframe = pd.read_csv("data/sh600000_history_k_data.csv", parse_dates=['date'])
    print(dataframe)
    # 为测试引入一些缺失值
    # 人为删除部分行数据，模拟缺失的交易日
    sample_indices = dataframe.sample(frac=0.5).index
    dataframe.loc[sample_indices, 'code'] = '000000'
    if 'code_name' in dataframe:
        dataframe.loc[sample_indices, 'code_name'] = 'ABCD'
    dataframe.loc[dataframe.sample(frac=0.05).index, 'close'] = np.nan
    dataframe.loc[dataframe.sample(frac=0.05).index, 'volume'] = np.nan
    print(dataframe)
    
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    # Add a strategy
    cerebro.addstrategy(TestStrategy)
    # Add the Data Feed to Cerebro
    add_data(dataframe, cerebro)
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    # Run over everything
    cerebro.run()