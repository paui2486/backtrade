import os, csv, sys
from datetime import datetime, timedelta
import yfinance as yf
## High Frequency Data ##

today = datetime.now().strftime('%Y-%m-%d')
seven_day_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

try:
    target = sys.argv[1]+'.TW'
    print(target)
except:
    exit('請輸入正確的股票代號')

fodel = target.replace('.TW','')
pd = '7d'
il = '1m'
data = yf.download(target,period='7d',interval='1m') ##時間長度 interval 時間單位 #PS 分鐘無法指定區段
# print(os.path.dirname(os.path.abspath(__file__)))
# rows = csv.reader(data)

loc = os.path.dirname(os.path.abspath(__file__))
ph = str(loc) + '\\'+fodel+'\\' + str(target) + '_'+seven_day_ago+'-'+today+'.csv' ## Path
print(ph)

# print(data)

# exit()
data.to_csv(ph, index=True, header = True)