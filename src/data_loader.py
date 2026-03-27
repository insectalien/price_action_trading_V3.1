import pandas as pd
import requests
from sqlalchemy import create_engine, text
import time

# 建立資料庫連線
engine = create_engine('postgresql://localhost:5432/Alien')

def get_multiple_data(stock_list):
    """
    一次處理多檔股票：檢查 SQL，若無則抓取 API 並存入 SQL。
    """
    all_data = {} # 存放所有股票的 DataFrame

    for stock_id in stock_list:
        table_name = f"stock_{stock_id}"
        
        try:
            # 1. 嘗試從 SQL 讀取
            df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
            print(f"{stock_id}: 從 SQL 讀取成功")
        
        except Exception:
            # 2. SQL 沒資料，抓 API
            print(f"{stock_id}: 資料庫無紀錄，開始從 API 抓取...")
            url = "https://api.finmindtrade.com/api/v4/data"
            parameter = {
                "dataset": "TaiwanStockPrice",
                "data_id": stock_id,
                "start_date": "2024-01-01"
            }
            
            response = requests.get(url, params=parameter)
            df = pd.DataFrame(response.json()["data"])
            
            # 3. 存入 SQL
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"{stock_id}: 已成功存入 SQL 表格 {table_name}")
            
            # 減少抓 API 速度，避免被封鎖
            time.sleep(1) 
        
        # 轉好日期格式並存入字典
        df['date'] = pd.to_datetime(df['date'])
        all_data[stock_id] = df 
    return all_data

def save_backtest_result(report_df, stock_id):
    """
    儲存前先刪除該股票的舊紀錄，確保資料不重複。
    """
    try:
        # 1. 建立一個 SQL 刪除指令：刪除這檔股票舊的回測紀錄
        # 這樣每次跑 main.py，資料庫永遠只會保留最新的一次實驗結果
        delete_query = text(f"DELETE FROM backtest_reports WHERE stock_id = '{stock_id}'")
        
        with engine.connect() as conn:
            conn.execute(delete_query)
            conn.commit() # 確認執行刪除

        #寫入新紀錄
        report_df.to_sql('backtest_reports', engine, if_exists='append', index=False)  # if_exists='append' 資料一直累加進去，不會覆蓋舊的
        print(f"♻️  已更新 {stock_id} 的回測紀錄 (舊資料已清理)")
    except Exception as e:
        print(f"❌ 儲存回測結果失敗: {e}")