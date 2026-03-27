from src.data_loader import save_backtest_result, get_multiple_data
from src.scanner import get_top_market_hot
from src.strategy import apply_engulfing_strategy
from src.backtester import Backtester  
import pandas as pd
import logging 
import datetime # 紀錄測試是什麼時候做的

# 設定日誌：同時輸出到螢幕與檔案
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("trading_system.log"), # 存成檔案
        logging.StreamHandler()                    # 顯示在螢幕
    ]
)

def run_trading_system():
    logging.info("Step 1: 正在抓取市場數據...")
    
    stocks = get_top_market_hot(top_n=5)  # 自動雷達 (先設5支試跑)
    data_dict = get_multiple_data(stocks)
    
    
    if not data_dict:
        logging.warning("沒有抓取到任何數據，請檢查資料庫連線或 API。")
        return

    for stock_id, df_raw in data_dict.items(): # 遍歷字典裡的每一檔股票進行回測
        logging.info(f"==== 正在分析股票：{stock_id} ====")
        logging.info("Step 2: 正在執行策略分析...")
        df_analyzed = apply_engulfing_strategy(df_raw)
    
        # 初始化回測器
        bt = Backtester(df_analyzed)
    
        # --- 實驗區：停損參數測試 ---
        results_to_save = [] # 準備一個清單來存放這一檔股票的所有實驗結果
        logging.info(f"[{stock_id}] 正在執行停損參數實驗並存入資料庫...")
        for sl_value in [0.01, 0.03, 0.05, 0.08, 0.10]:
            report = bt.run_advanced(stop_loss=sl_value, take_profit=0.10)
            # 加一個判斷，避免沒交易時噴錯
            if report and "Total Trades" in report:
                print(f"停損設為 {sl_value*100:>2.0f}% | 勝率: {report['Win Rate']} | 總報酬: {report['Cumulative Return']}")
                # 建立一筆完整的紀錄資料
                record = {
                    "test_date": datetime.datetime.now(), # 測試執行的時間
                    "stock_id": stock_id,
                    "stop_loss": sl_value,
                    "take_profit": 0.10,
                    "win_rate": float(report['Win Rate'].strip('%')) / 100, # 轉成數字好運算
                    "total_return": float(report['Cumulative Return'].strip('%')) / 100,
                    "total_trades": report['Total Trades']
                }
                results_to_save.append(record)
        # 將這一檔股票的所有實驗結果轉成 DataFrame 並存入 SQL
        if results_to_save:
            report_df = pd.DataFrame(results_to_save)
            save_backtest_result(report_df, stock_id)
            print(f"✅ {stock_id} 的 5 組實驗結果已存入資料庫！")
        
        
        
        print(f"--- {stock_id} 實驗結束 ---\n")

        # 執行正式報告
        print(f"Step 3: Running Final Backtest Report for {stock_id}...")
        stats = bt.run_advanced(take_profit=0.05, stop_loss=0.1)

        # 輸出結果統計
        num_bull = df_analyzed['bull_signal'].sum()
        print(f"Analysis Complete: Found {num_bull} Buy signals for {stock_id}.")
        print(f"\n--- {stock_id} Strategy Performance Report ---")
        for key, value in stats.items():
            print(f"{key}: {value}")
        print("-----------------------------------\n")
    
        # 6. 視覺化
        #logging.info("生成視覺化圖表...")
        #plot_signals(df_analyzed)

if __name__ == "__main__":
    try:
        run_trading_system()
    except Exception as e:
        logging.error(f"❌ 程式執行發生錯誤：{e}", exc_info=True)  # 紀錄錯誤細節