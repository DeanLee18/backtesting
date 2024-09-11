import os
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
    if 'time' in dataframe:
        dataframe['time'] = pd.to_datetime(dataframe['time'], format='%Y%m%d%H%M%S%f')
        dataframe.set_index('time', inplace=True)
    elif 'date' in dataframe:
        dataframe.set_index('date', inplace=True)
    elif 'datetime' in dataframe:
        dataframe.set_index('datetime', inplace=True)
    # 创建一个空的数据框用于对齐数据
    aligned_data = pd.DataFrame(index=dataframe.index.unique())
    processed_data = {}

    # 处理每一个股票代码的数据
    for code_name in dataframe['code_name'].unique():
        stock_data = dataframe.query(f"code_name == '{code_name}'")
        stock_data_aligned = pd.merge(aligned_data, stock_data, left_index=True, right_index=True, how='left')

        # 对齐数据框并填补缺失值
        stock_data_aligned = pd.merge(aligned_data, stock_data, left_index=True, right_index=True, how='left')
        stock_data_aligned[['volume']] = stock_data_aligned[['volume']].fillna(0)
        stock_data_aligned[['code', 'open', 'high', 'low', 'close', 'code_name']] = \
            stock_data_aligned[['code', 'open', 'high', 'low', 'close', 'code_name']].fillna(method='pad')
        processed_data[code_name] = stock_data_aligned

    # 将处理后的数据加载到 cerebro 中
    for name, data in processed_data.items():
        datafeed = bt.feeds.PandasData(dataname=data)  # 转换为 backtrader 的 PandasData
        cerebro.adddata(datafeed, name=str(name))  # 加载到 cerebro 实例中

if __name__ == '__main__':
    # Load data
    data_folder = './data/CSI_300_15minsk_since2017/k_data/'
    dataframes = []
    for i, file in enumerate(os.listdir(data_folder)):
        if i >= 5:
            break
        df = pd.read_csv(os.path.join(data_folder, file))
        dataframes.append(df)
    dataframe = pd.concat(dataframes, ignore_index=True)
    
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