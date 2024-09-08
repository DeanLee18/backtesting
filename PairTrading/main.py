from pairSearch import find_cointegrated_pairs
from tradingModel import simplePairTradingModel
import pandas as pd
import numpy as np
import pickle

def main():
 
    # Step 1: Get the data
    data_dict = pd.read_csv(r'PairTrading\test_data\test_data.csv', parse_dates=['datetime'])
    data_dict.set_index('datetime', inplace=True)
    # split the data by take 20 random columns to check feasibilty
    random_columns = np.random.choice(data_dict.columns, size=10, replace=False)
    data_subset = data_dict[random_columns]
    
    print(data_subset.head())
    print(data_subset.keys())
    
    
    # Step 2: Find cointegrated pairs
    # output: List of tuples, each tuple contains two cointegrated pairs (code1, code2)
    cointegrated_pairs = find_cointegrated_pairs(data_subset).find_cointegrated_pairs()
    
    # Step 3: Generate trading signals
    # signal: list of integers with values -1, 0, 1, 2
    # -1: sell ratio, 1: buy ratio, 0: clear ratio, 2: no action
    # sell ratio: secruity 1 is overvalued, secruity 2 is undervalued, buy security 2 and sell security 1 (if security 1 is long position)
    # buy ratio: secruity 1 is undervalued, secruity 2 is overvalued, buy security 1 and sell security 2 (if security 2 is long position)
    # clear ratio: clear position(if both security 1 and security 2 are long position)
    # no action: no action
    
    for pair in cointegrated_pairs:
        series1 = data_dict[pair[0]]
        series2 = data_dict[pair[1]]
        model = simplePairTradingModel(series1, series2)
        signals = model.generate_signals()
        print(f"Pair: {pair}")
        print(signals)
        print("\n")

if __name__ == "__main__":
    main()