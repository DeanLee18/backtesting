import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

import sys
sys.path.append("/PairTrading")


def calculate_z_score(series1, series2, split_ratio):
    ratio = series1 / series2
    # print(ratio.min(), ratio.max())
    split_index = int(len(ratio) * split_ratio)
    sub_ratio = ratio[:split_index]
    mean_5 = sub_ratio.rolling(window=3).mean()
    mean_60 = sub_ratio.rolling(window=10).mean()
    std_60 = sub_ratio.rolling(window=10).std()
    z_score = (mean_5 - mean_60) / std_60
    return ratio, z_score

def generate_signals(z_score, threshold=1,threshold2=0.5):
    signals = pd.Series(index=z_score.index,data=np.zeros(len(z_score)) -2)
    signals[z_score > threshold] = -1
    signals[z_score < -threshold] = 1
    signals[(z_score >= -threshold2) & (z_score <= threshold2)] = 0
    return signals

def plot_trading_charts(series1, series2, split_ratio=1, threshold=1,save_dir = None):
    ratio, z_score = calculate_z_score(series1, series2, split_ratio)
    signals = generate_signals(z_score, threshold,0.5)
    # print(np.unique(signals, return_counts=True))
    
    # Ensure the indices align
    signals = signals.reindex(ratio.index)
    
    fig, axs = plt.subplots(5, 1, figsize=(12, 24))
    
    # Plot 1: series1 and series2
    axs[0].plot(series1, label='Series1')
    axs[0].plot(series2, label='Series2')
    axs[0].set_title('Series1 and Series2')
    axs[0].legend()
    
    # Plot 2: Ratio
    axs[1].plot(ratio, label='Ratio')
    axs[1].axhline(ratio.mean(), color='black', linestyle='--', label='Mean')
    axs[1].set_title('Ratio')
    axs[1].legend()
    
    # Plot 3: Z-Score
    axs[2].plot(z_score, label='Z-Score')
    axs[2].axhline(z_score.mean(), color='black', linestyle='--', label='Mean')
    axs[2].axhline(1, color='red', linestyle='--', label='Upper Threshold')
    axs[2].axhline(-1, color='green', linestyle='--', label='Lower Threshold')
    axs[2].set_title('Z-Score')
    axs[2].legend()
    
    # Plot 4: Signals with Ratio Overlay
    axs[3].plot(ratio, label='Ratio')
    axs[3].scatter(signals[signals == -1].index, ratio[signals == -1], color='blue', label='Sell Signal (-1)')
    axs[3].scatter(signals[signals == 1].index, ratio[signals == 1], color='red', label='Buy Signal (1)')
    axs[3].scatter(signals[abs(signals) == 0].index, ratio[signals == 0], color='black', label='Clear Position (0)')
    axs[3].scatter(signals[signals == -2].index, ratio[signals == -2], color='green', label='no action (-2)')
    axs[3].set_title('Signals with Ratio Overlay')
    axs[3].legend()
    # Plot 5: Signal Markers
    axs[4].plot(series1, label='Series1')
    axs[4].plot(series2, label='Series2')
    axs[4].scatter(signals[signals == -1].index, series2[signals == -1], marker='^', color='red', label='Buy Signal (-1)')
    axs[4].scatter(signals[signals == -1].index, series1[signals == -1], marker='v', color='green', label='Sell Signal (1)')
    axs[4].scatter(signals[signals == 1].index, series1[signals == 1], marker='^', color='red', label='Buy Signal (1)')
    axs[4].scatter(signals[signals == 1].index, series2[signals == 1], marker='.', color='green', label='Sell Signal (-1)')
    axs[4].scatter(signals[signals == 0].index, series1[signals == 0], marker='.', color='green', label='Sell Signal (0)')
    axs[4].scatter(signals[signals == 0].index, series2[signals == 0], marker='.', color='green', label='Sell Signal (0)')
    axs[4].set_title('Signal Markers')
    axs[4].legend()

    
    plt.tight_layout()
    if save_dir:
        plt.savefig(save_dir)
    plt.show()

# Example usage
if __name__ == "__main__":
    from pairSearch import check_cointegration
    # series2 = pd.Series(np.cumsum(np.random.normal(0,1,1000))) + 50 
    # series1 = 5 + series2 + pd.Series(np.random.normal(0, 1, 1000)) 
    # print(check_cointegration(series1, series2))
    # # series2 = series2 + pd.Series(np.random.normal(0, 1, 100)) * 2 
    test_data = pd.read_csv(r'PairTrading\test_data\test_data.csv')
    cointegrated_pairs = pd.read_pickle(r'PairTrading\test_data\cointegrated_pairs.pkl')
    for i in cointegrated_pairs:
        series1 = test_data[i[0]]
        series2 = test_data[i[1]]
        # print(series1)
        # print(series2)
        # print(series1/series2)
        plot_trading_charts(series1, series2,save_dir="./PairTrading/visualization/%s.png"%('_'.join(i)))

