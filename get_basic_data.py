import yfinance as yf
import time

stk_list = ['GRMN']
# 先測試一檔試看看
stock = yf.Ticker('GRMN')

# 取得損益表，執行看看結果
stock.financials
print(stock.financials)
time.sleep(1)

# 取得資產負債表，執行看看結果
stock.balance_sheet
print(stock.balance_sheet)
time.sleep(1)
# 取得現金流量表，執行看看結果
stock.cashflow
print(stock.cashflow)
time.sleep(1)
failed_list = []
# 開始迴圈抓資料囉！
# for i in stk_list:
#     try:
#         # 打印出目前進度
#         print('processing: ' + i)
#         # 填入股票代碼後直接下載成 csv 格式
#         stock = yf.Ticker(i)
#         stock.financials.to_csv('profit_loss_account_'+i+'.csv')
#         stock.balance_sheet.to_csv('balance_sheet_'+i+'.csv')
#         stock.cashflow.to_csv('cash_flow_'+i+'.csv')
#         # 停一秒，再抓下一檔，避免對伺服器造成負擔而被鎖住
#         time.sleep(1)
#     except :
#         failed_list.append(i)
#         continue