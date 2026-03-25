import pandas as pd
from FinMind.data import DataLoader # 注意這裡根據你之前的測試可能要用大寫 Data
import datetime

def get_top_market_hot(top_n=10):
    """
    自動抓取全市場成交金額前 N 名的股票清單。
    """
    dl = DataLoader()
    # 如果有申請 Token 再加上 (沒加次數受限)
    # dl.login_by_token(api_token="自己的Token")
    
    try:
        # 使用函數：taiwan_stock_tick_snapshot
        # 抓取全市場當下（或收盤）所有股票狀態
        df = dl.taiwan_stock_tick_snapshot()
        
        if df is None or df.empty:
            print("[雷達回報] 目前非交易時段或 API 未回傳，啟動熱門穩定名單。")
            return ["2330", "2317", "2454", "2603", "2609"]
        
        # 強制轉小寫避免 'Amount' vs 'amount'
        df.columns = [col.lower() for col in df.columns]
        
        if 'amount' in df.columns and 'stock_id' in df.columns:
            # 篩選：只抓一般股票 (通常代號為 4 碼，排除權證與 ETF)
            # 官方數據中 stock_id 是字串，過濾長度等於 4 的
            df = df[df['stock_id'].str.len() == 4]

            # 排序：根據 'amount' (當日累計成交金額) 降序排列
            # amount = 該標的截至目前的總成交金額
            df_hot = df.sort_values(by='amount', ascending=False)

            # 取得前 N 名股票代號
            top_stocks = df_hot.head(top_n)['stock_id'].tolist()

            print(f"市場雷達掃描完成！今日資金最集中標的：{top_stocks}")
            return top_stocks
        else:
            print("找不到成交金額欄位，使用穩定名單")
            return ["2330", "2317", "2454", "2603", "2609"]
        

    except Exception as e:
        print(f"[雷達提醒] API 暫時無法解析數據 ({e})，已切換至穩定名單。")
        return ["2330", "2317", "2454", "2603", "2609"]

if __name__ == "__main__":
    # 測試用：直接執行此檔案可以看結果
    print(get_top_market_hot(5))