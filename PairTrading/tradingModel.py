import pandas as pd
import numpy as np


# Why use window size 5 and 60: diminish the impact of outliers and noise
# Why use z-score: to normalize the data and make it easier to compare
# Why use split_ratio: to avoid look-ahead bias

class simplePairTradingModel:
    def __init__(self, series1, series2, split_ratio=1, window_size_now=5,window_size_long=60):
        self.series1 = series1
        self.series2 = series2
        self.split_ratio = split_ratio
        self.window_size_now = window_size_now
        self.window_size_long = window_size_long

    def calculate_z_score(self, series1, series2):
        # Step 1: 计算两个数组的比值
        ratio = series1 / series2
        
        # Step 2: 根据切分比例取子数组
        split_index = int(len(ratio) * self.split_ratio)
        sub_ratio = ratio[:split_index]
        
        # Step 3: 计算滚动均值和方差
        mean_5 = sub_ratio.rolling(window=self.window_size_now).mean()
        mean_60 = sub_ratio.rolling(window=self.window_size_long).mean()
        std_60 = sub_ratio.rolling(window=self.window_size_long).std()
        
        # Step 4: 计算 z-score
        z_score = (mean_5 - mean_60) / std_60
        
        # Step 5: 输出 z-score
        return z_score

    def generate_signals(self):
        z_score = self.calculate_z_score(self.series1, self.series2)
        signals = []
        # TODO: model the trading signals based on the z-score
        for z in z_score:
            '''
            -1 : sell ratio
            1: buy ratio
            0: clear ratio
            2: no action
            '''
            if z > 1:
                # secruity 1 is overvalued
                # secruity 2 is undervalued
                # buy security 2 and sell security 1 (if security 1 is long position)
                signals.append(-1)
            elif z < -1:
                # secruity 1 is undervalued
                # secruity 2 is overvalued
                # buy security 1 and sell security 2 (if security 2 is long position)
                signals.append(1)
            elif abs(z) < 0.5:
                # clear position(if both security 1 and security 2 are long position)
                signals.append(0)
            else:
                # no action
                signals.append(-2)
        return signals

if __name__ == "__main__":
    # Example usage
    # Example 1: Test with sample data
    series1 = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    series2 = pd.Series([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])

    model = simplePairTradingModel(series1, series2, split_ratio=1, window_size_now=1, window_size_long=3)
    signals = model.generate_signals()
    print(signals)
    
    # Example 2: Test with different data
    series1 = pd.Series([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    series2 = pd.Series([50, 100, 150, 200, 250, 300, 350, 400, 450, 500])

    model = simplePairTradingModel(series1, series2, split_ratio=1, window_size_now=1, window_size_long=3)
    signals = model.generate_signals()
    print(signals)
