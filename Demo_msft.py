import os
from datetime import datetime
import backtrader as bt
import yfinance as yf
from Strategy import *

# datasource = 'GRMN.csv'
datasource = '0050.TW.csv'

## dowmloaddata Start
# target = '0050.TW'
# data = yf.download(target, start="2020-01-01", end="2022-01-01")
# loc = os.path.dirname(os.path.abspath(__file__))
# ph = str(loc) + '\\' + str(target) + '.csv' ## Path
# print(ph)

# datasource = str(target) + '.csv'

# data.to_csv(ph, index=True, header = True)
## dowmloaddata End

##analyzing data
cerebro = bt.Cerebro()
cerebro.broker.setcash(100000.0) ## 初始資金 Initial funding 

# cerebro.addstrategy(SmaCross)
cerebro.addstrategy(K_80_20_buy_sell)

data0 = bt.feeds.YahooFinanceData(dataname=datasource, fromdate=datetime(2020, 1, 1),todate=datetime(2020, 12, 30)) ## 確認 可動
# data0 = bt.feeds.PandasData(dataname=yf.download("MSFT", start="2023-01-01", end="2023-06-30")) ## 直接網路抓資料 ## 確認 可動 但是頻率不宜太高
# data0 = bt.feeds.GoogleFinanceData(dataname='2330.TW',fromdate=datetime(2023, 1, 1),todate=datetime(2023, 12, 31),exchange='TPE') ## 測試不可用
cerebro.adddata(data0)

cerebro.run()
##analyzing data
## draw picture
cerebro.plot()
## draw picture