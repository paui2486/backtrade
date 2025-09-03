import pandas as pd
import requests
# from io import StringIO
import time, sys, os,time, gc
import yfinance as yf
# from bs4 import BeautifulSoup as bs
from lxml import etree,html
from functools import cache
from datetime import datetime,timedelta
# import datetime
import backtrader as bt
from Strategy import *


# Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota Kappa Lambda Mu NU Xi Omicron Pi Rho Sigma Tau Upsilon Phi Chi Psi Omega
#            Emma

# @cache
def analyze_report(year, month):
    gc.enable()
    if year > 1990:
        year -= 1911

    dfm = []
    lr = 3# len_range
    for base in range(0,lr): # 6 9 12
        imonth = int(month) + base
        print(imonth)
        dfs = pd.read_csv(f"TW_revenue\\tmp_tw_revenue_{year}_{str(imonth)}.csv",index_col=None)

        # pd.set_option('display.max_columns', None)#显示所有列
        # pd.set_option('display.max_rows', None)#显示所有行
        dfm.append(dfs)
        print(dfs)
        # print(dfs.index)
        # print(dfs.columns)
        # print(dfs.columns.get_level_values(1))
        # print(dfs['code'])
        # print(type(dfs['code']))
        # print(dfs.loc[dfs['code'] == 1104])
        # for dfsc in dfs['code']:
        #     print(dfsc)
    
    cl = []## code_list
    tco = [] #The chosen one
    for dfmo in dfm[0]['code']:
        cl.append(dfmo)
        tco.append(dfmo)

    for cli in cl:
        # print(dfm[beta].loc[dfm[beta]['code'] == 1104,['上月比較 增減(%)','去年同月 增減(%)']])
        ciadlm = 0 #Comparative increase and decrease last month 上月比較 增減(%)
        smlyiod = 0 #Same month last year Increase or decrease 去年同月 增減(%)
        # print(cli)
        for beta in range(0,lr):
            alpha = dfm[beta].loc[dfm[beta]['code'] == cli]
            # print(type(alpha['上月比較 增減(%)']))
            # print((alpha['上月比較 增減(%)'].values[0]))
            if alpha['上月比較 增減(%)'].values[0] >= ciadlm: ## 這是大幅成長
                ciadlm = alpha['上月比較 增減(%)'].values[0]
            # if alpha['上月比較 增減(%)'].values[0] >= 0.5: ## 這才是這個月比上個月好 (這會不會太寬鬆)
                # pass
            else:
                try:
                    tco.remove(cli)
                except:
                    pass
    # print(tco)
                    
    for tec_m in tco:
        Delta = dfm[0].loc[dfm[0]['code'] == tec_m]
        d_code = Delta['code'].values[0]
        d_name = Delta['公司名稱'].values[0]
        print(f"{d_code} {d_name}")
        
        code_industry_type = get_code_industry_info(d_code,d_name)
        
        if '科技' in code_industry_type or '電腦' in code_industry_type or '半導體' in code_industry_type:
        # if '科技' in code_industry_type or '半導體' in code_industry_type:

            try:
                tco.remove(tec_m)
            except:
                pass

    for mtco in tco:
        # Gamma = dfm[0].loc[dfm[0]['code'] == mtco]
        Gamma = dfm[0].loc[dfm[0]['code'] == mtco,['code','公司名稱','備註']]
        print("Gamma")
        print(Gamma) ## 營收連續成長觀察股價發酵
        print("Gamma")

    return tco

@cache
def get_code_industry_info(d_code,d_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(f"https://isin.twse.com.tw/isin/class_main.jsp?owncode={d_code}&stockname={d_name}&isincode=&market=&issuetype=&industry_code=&Page=1&chklike=Y", headers=headers)
    # print(r.text)
    ## 暴力解析
    r_tmp = r.text.split('股票')
    r_tmp_v1 = r_tmp[1].split('</td>')
    r_tmp_v2 = r_tmp_v1[1].replace('<td bgcolor=#FAFAD2>','').replace(' ','').replace('\n','')
    ## 暴力解析
    print(r_tmp_v2)
    # exit("CIT")
    return r_tmp_v2

def dowmload_code_data(year,code):
    try:
        target = str(code)+'.TW'
        print(target)
    except:
        exit('請輸入正確的股票代號')
    # target = '0050.TW'
    fodel = target.replace('.TW','')
    sd = f'{year}-01-01'
    ed = f'{year}-12-31'
    data = yf.download(target, start=sd, end=ed)
    print('data dowmload finish')
    # data = yf.download(target, start=sd, end=ed,proxy=f"{ip}:{port}")
    # print(os.path.dirname(os.path.abspath(__file__)))
    loc = os.path.dirname(os.path.abspath(__file__))

    if os.path.isdir(str(loc) + '\\'+fodel):
        # print("目錄存在。")
        pass
    else:
        os.mkdir(str(loc) + '\\'+fodel)
    
    # ph = str(loc) + '\\'+fodel+'\\' + str(target) + '.csv' ## Path
    ph = str(loc) + '\\'+fodel+'\\' + str(target)+'_'+ sd +'_'+ ed +'.csv' ## Path

    print(ph)

    # exit()
    data.to_csv(ph, index=True, header = True)
    time.sleep(10)

def backtrader_strategy(ar,year,month,strategy):
    
    base_bt = datetime.strptime(f'{year}-{month}', "%Y-%m")
    start_year,start_month = (base_bt + timedelta(days=92)).strftime("%Y-%m").split('-')
    end_year,end_month = (base_bt + timedelta(days=180)).strftime("%Y-%m").split('-')
    
    print(f"CODE:{ar}")
    code = ar
    # code = tmp_ar['code']
    # company_name = tmp_ar['公司名稱']
    # note = tmp_ar['備註']

    datasource = f'{code}\\{code}.TW_{year}-01-01_{year}-12-31.csv'

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0) ## 初始資金 Initial funding 

    cerebro.addstrategy(strategy) ## 添加策略 K_80_20_buy_sell(這是策略)
    cerebro.broker.setcommission(commission = 0.1425 / 100) ## 台股手續費

    try:
        data0 = bt.feeds.YahooFinanceData(dataname=datasource, fromdate=datetime(int(start_year), int(start_month), 1),todate=datetime(int(end_year), int(end_month), 30)) ## 確認 可動
    except:
        data0 = bt.feeds.YahooFinanceData(dataname=datasource, fromdate=datetime(int(start_year), int(start_month), 1),todate=datetime(int(end_year), int(end_month), 28)) ## 確認 可動

    cerebro.adddata(data0) ## 資料丟入模型

    cerebro.run() ## analyzing data
     
    cerebro.plot() ## draw picture plotname=f"{str(code)}.TW_{str(year)}-{str(month)}_{str(year)}-{str(month+2)}.png"

year = int(sys.argv[1]) ## 明國西元年皆可
month = str(sys.argv[2]) ## 月份 不要補0

# backtrader_strategy('1104',int(year),int(month),K_80_20_buy_sell) ##目標 年 月 策略(K_80_20_buy_sell)

# dl = False
dl = True

ar = analyze_report(year, month)
print("\n\n Enter Backtrader Analyze")
if dl == True:
    if int(month) +6 > 12:
        tmp_year = int(year) +1
        print(f"**{year}**")
    else:
        pass

    for tmp_ar in ar:
        print(tmp_ar)
        
        if os.path.isfile(f"{tmp_ar}\\{tmp_ar}.TW_{tmp_year}-01-01_{tmp_year}-12-31.csv"):
            pass
        else:
            dowmload_code_data(tmp_year,tmp_ar)
        # exit("Pause")
else:
    pass

## 有目標清單 資料 後面有兩條路 
#A 直接讀 csv 看趨勢 B
#B backtrade 直接回測績效

for tmp_ar in ar:

    backtrader_strategy(tmp_ar,int(year),int(month),K_80_20_buy_sell) ##目標 年 月 策略(K_80_20_buy_sell)
    exit('BS')