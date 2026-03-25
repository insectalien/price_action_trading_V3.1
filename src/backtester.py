import pandas as pd

class Backtester:
    def __init__(self, df):
        self.df = df.reset_index(drop=True)
    def __repr__(self):
        return f"<TradingBacktester for {len(self.df)} rows of data>"

    def run_simple(self, holding_days=5):
        """執行簡單回測"""
        returns = []
        buy_indices = self.df[self.df['bull_signal']].index
        for idx in buy_indices:
            sell_idx = idx + holding_days
            if sell_idx < len(self.df):
                buy_price = self.df.loc[idx, 'close']
                sell_price = self.df.loc[sell_idx, 'close']
                returns.append((sell_price - buy_price) / buy_price)
        return self._calculate_stats(returns)

    def run_advanced(self, take_profit=0.05, stop_loss=0.03):
        """執行進階回測"""
        returns = []
        in_position = False
        entry_price = 0
        for i in range(len(self.df)):
            if not in_position and self.df.loc[i, 'bull_signal']:
                in_position = True
                entry_price = self.df.loc[i, 'close']
                continue
            if in_position:
                return_pct = (self.df.loc[i, 'close'] - entry_price) / entry_price
                if return_pct >= take_profit or return_pct <= -stop_loss or self.df.loc[i, 'bear_signal']:
                    returns.append(return_pct)
                    in_position = False
        return self._calculate_stats(returns)

    def _calculate_stats(self, returns):
        """內部私有函數：計算統計指標"""
        if not returns: return {"Error": "No trades"}
        df_ret = pd.Series(returns)
        return {
            "Total Trades": len(returns),
            "Win Rate": f"{(df_ret > 0).mean():.2%}",
            "Avg Return": f"{df_ret.mean():.2%}",
            "Cumulative Return": f"{(1 + df_ret).prod() - 1:.2%}"
        }