import yfinance as yf
import time,sys
import pandas as pd
from functools import cache

code = sys.argv[1]

@cache
def get_company_info(code):
    # 取得個股公司資料的語法，先測試一檔看看
    # stk_basic_data = yf.Ticker('AAPL').info
    stk_basic_data = yf.Ticker(f'{code}.TW').info
    print(f"{stk_basic_data}")
    # 將 yfinance 有提供的數據項目取出存在 info_columns，它將會成為 stk_info_df 這張總表的欄位項目
    info_columns = list(stk_basic_data.keys())
    print(f"\n{info_columns}")
    # 創立一個名為 stk_info_df 的總表，用來存放所有股票的基本資料！其中 stk_list 是我們先前抓到的股票代碼喔！
    # stk_info_df = pd.DataFrame(index = stk_list.sort_values(), columns = info_columns)

# 創立一個紀錄失敗股票的 list
# failed_list = []

get_company_info(code)