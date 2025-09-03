import os, sys, time
from datetime import datetime, timedelta
# from google_proxy_net import requests_randow_proxy
import yfinance as yf

# mode = 3
# ip, port = requests_randow_proxy(mode)

try:
    target = sys.argv[1]+'.TW'
    print(target)
except:
    exit('請輸入正確的股票代號')
# target = '0050.TW'
fodel = target.replace('.TW','')
sd = '2023-01-01'
ed = '2023-12-31'
data = yf.download(target, start=sd, end=ed)
# data = yf.download(target, start=sd, end=ed,proxy=f"{ip}:{port}")
# print(os.path.dirname(os.path.abspath(__file__)))
loc = os.path.dirname(os.path.abspath(__file__))
# ph = str(loc) + '\\'+fodel+'\\' + str(target) + '.csv' ## Path
ph = str(loc) + '\\'+fodel+'\\' + str(target)+'_'+ sd +'_'+ ed +'.csv' ## Path

print(ph)

# exit()
data.to_csv(ph, index=True, header = True)
# time.sleep(5)