import pandas as pd
import requests
from io import StringIO
import time,sys

def monthly_report(year, month):
    
    # 假如是西元，轉成民國
    if year > 1990:
        year -= 1911
    
    url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'_0.html'
    if year <= 98:
        url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'.html'
    
    # 偽瀏覽器
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    
    # 下載該年月的網站，並用pandas轉換成 dataframe
    ## net
    r = requests.get(url, headers=headers)
    r.encoding = 'big5'
    # print(f"** {r.text} **")
    with open(f'TW_revenue\\tmp_tw_revenue_{year}_{month}.txt', 'w',encoding='utf-8') as f:
        f.write(r.text)
    
    dfs = pd.read_html(StringIO(r.text), encoding='big-5')
    ## net

    ## loc
    # with open('tmp_tw_revenue.txt', 'r', encoding="utf8") as f:
    #     data = f.read()
    # dfs = pd.read_html(StringIO(data), encoding='utf-8')
    ## loc

    pd.set_option('display.max_columns', None)#显示所有列
    pd.set_option('display.max_rows', None)#显示所有行

    df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
    
    if 'levels' in dir(df.columns):
        df.columns = df.columns.get_level_values(1)
        # print(f"** {df.columns} **")
    else:
        df = df[list(range(0,10))]
        column_index = df.index[(df[0] == '公司 代號')][0]
        df.columns = df.iloc[column_index]
        print(f"** {df.columns} **")
    
    df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
    df = df[~df['當月營收'].isnull()]
    df = df[df['公司 代號'] != '合計']
    
    # 偽停頓
    # time.sleep(2)

    return df

year = int(sys.argv[1]) ## 明國西元年皆可
month = str(sys.argv[2]) ## 月份 不要補0

mr = monthly_report(year, month)

# print(mr)