import matplotlib.pyplot as plt
import pandas as pd

def plot_signals(df):
    """
    將價格走勢、均線與 PA 訊號畫成圖表
    """
    df['date'] = pd.to_datetime(df['date'])
    
    plt.figure(figsize=(14, 7))
    plt.plot(df['date'], df['close'], label='Close Price', color='gray', alpha=0.3)
    plt.plot(df['date'], df['ma20'], label='MA20', color='orange', linestyle='--', alpha=0.8)

    # 標註買賣訊號
    bull_signals = df[df['bull_signal']]
    bear_signals = df[df['bear_signal']]
    
    plt.scatter(bull_signals['date'], bull_signals['close'], color='green', label='Bullish', marker='^', s=80)
    plt.scatter(bear_signals['date'], bear_signals['close'], color='red', label='Bearish', marker='v', s=80)

    plt.title('Professional Trading System - TSMC (2330)')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.show()