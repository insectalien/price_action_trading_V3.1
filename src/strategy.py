import pandas as pd

def apply_engulfing_strategy(df):
    """
    價格行為學：吞沒形態策略 ＋ 20MA 趨勢過濾
    """
    # 1. 基礎特徵
    df['is_bullish'] = (df['close'] > df['open']).astype(int)
    df['body_size'] = abs(df['close'] - df['open'])
    df['ma20'] = df['close'].rolling(window=20).mean()    # 計算 20 日均線 (SMA 20)
    
    # 2. 加入成交量過濾 (Volume Filter)
    df['vol_ma5'] = df['Trading_Volume'].rolling(window=5).mean()
    df['vol_filter'] = df['Trading_Volume'] > df['vol_ma5']
    
    # 3. 平移數據看昨天
    df['prev_is_bullish'] = df['is_bullish'].shift(1)
    df['prev_body_size'] = df['body_size'].shift(1)
    
    # 4. 識別多空吞沒 (加上 MA 與 Volume 過濾)
    # 只有收盤價在均線之上，才考慮多頭訊號
    df['bull_signal'] = (df['prev_is_bullish'] == 0) & \
                        (df['is_bullish'] == 1) & \
                        (df['body_size'] > df['prev_body_size']) & \
                        (df['close'] > df['ma20']) & \
                        (df['vol_filter'] == True)
    # 只有收盤價在均線之下，才考慮空頭訊號
    df['bear_signal'] = (df['prev_is_bullish'] == 1) & \
                        (df['is_bullish'] == 0) & \
                        (df['body_size'] > df['prev_body_size']) & \
                        (df['close'] < df['ma20'])
    
    return df