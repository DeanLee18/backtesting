from statsmodels.tsa.stattools import coint
import pandas as pd
import numpy as np
from itertools import combinations
import os
import pandas as pd
from tqdm import tqdm
import pickle

def check_cointegration(series1, series2, threshold=0.05):
    # Convert the pandas series to numpy arrays
    array1 = series1.to_numpy()
    array2 = series2.to_numpy()

    # Calculate the cointegration between the two series
    _, p_value, _ = coint(array1, array2)

    # Check the cointegration level based on the p-value and threshold
    return p_value < threshold

def check_pair(pair, data_dict, threshold):
    sec1, sec2 = pair
    series1 = data_dict[sec1]
    series2 = data_dict[sec2]
    return (sec1, sec2) if check_cointegration(series1, series2, threshold) else None

def find_cointegrated_pairs(data_dict, threshold=0.05):
    cointegrated_pairs = []
    pairs = list(combinations(data_dict.keys(), 2))
    
    for pair in pairs:
        result = check_pair(pair, data_dict, threshold)
        if result is not None:
            cointegrated_pairs.append(result)
    
    return cointegrated_pairs

def read_csv_files(directory):
    data_dict = {}
    
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            # Extract the first component of the file name
            key = filename.split("_")[0]
            
            # Read the CSV file
            filepath = os.path.join(directory, filename)

            df = pd.read_csv(filepath)
            df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d%H%M%S%f')
            df.set_index('datetime', inplace=True)
            # Drop the original 'date' and 'time' columns
            df.drop(columns=['date', 'time'], inplace=True)
            # Drop duplicate indices
            df = df[~df.index.duplicated(keep='first')]
            
            # Create a pd.Series with the 'close' column
            series = pd.Series(df['close'].values, index=df.index, name=key)
            
            # Add the series to the dictionary
            data_dict[key] = series
    
    # Merge all series into a single DataFrame based on the overlapping index
    merged_df = pd.concat(data_dict.values(), axis=1, join='inner')
    merged_df.columns = data_dict.keys()
    
    return merged_df

class find_cointegrated_pairs:
    def __init__(self, data_dict, threshold=0.05):
        self.data_dict = data_dict
        self.threshold = threshold

    def check_cointegration(self, series1, series2):
        # Convert the pandas series to numpy arrays
        array1 = series1.to_numpy()
        array2 = series2.to_numpy()

        # Calculate the cointegration between the two series
        _, p_value, _ = coint(array1, array2)

        # Check the cointegration level based on the p-value and threshold
        return p_value < self.threshold

    def check_pair(self, pair):
        sec1, sec2 = pair
        series1 = self.data_dict[sec1]
        series2 = self.data_dict[sec2]
        return (sec1, sec2) if self.check_cointegration(series1, series2) else None

    def find_cointegrated_pairs(self):
        cointegrated_pairs = []
        pairs = list(combinations(self.data_dict.keys(), 2))
        
        for pair in tqdm(pairs):
            result = self.check_pair(pair)
            if result is not None:
                cointegrated_pairs.append(result)
        
        return cointegrated_pairs
    
# Example usage
if __name__ == "__main__":
    # data_dict = {
    #     'AAPL': pd.Series([1, 2, 3, 4, 5]),
    #     'MSFT': pd.Series([2, 3, 4, 5, 6]),
    #     'GOOGL': pd.Series([5, 6, 7, 8, 9])\

    # }

    # cointegrated_pairs = find_cointegrated_pairs(data_dict)
    # print(cointegrated_pairs)
    # merged_data = read_csv_files(r"C:\Users\huilo\Downloads\CSI_300_15minsk_since2017\k_data")
    # merged_data.to_csv("./test_data.csv")
    
    merged_data = pd.read_csv(r'PairTrading\test_data\test_data.csv', parse_dates=['datetime'])
    merged_data.set_index('datetime', inplace=True)
    print(merged_data.head())
    print(merged_data.keys())
    
    # split the data by take 20 random columns to check feasibilty
    random_columns = np.random.choice(merged_data.columns, size=10, replace=False)
    data_subset = merged_data[random_columns]
    coint_model = find_cointegrated_pairs(data_subset)
    cointegrated_pairs = coint_model.find_cointegrated_pairs()
    print(cointegrated_pairs)

    # Dump the result as a binary object
    with open(r'PairTrading\test_data\cointegrated_pairs.pkl', 'wb') as f:
        pickle.dump(cointegrated_pairs, f)