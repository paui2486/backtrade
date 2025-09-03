import pandas as pd
# import requests
from io import StringIO
import sys


def analyze_report(year, month):
    if year > 1990:
        year -= 1911

    dfm = []

    for base in range(0,12):
        imonth = int(month) - base
        print(imonth)
        try:
            with open(f'TW_revenue\\tmp_tw_revenue_{year}_{str(imonth)}.txt', 'r', encoding="utf8") as f:
                data = f.read()
            dfs = pd.read_html(StringIO(data), encoding='utf-8') # ,index_col=0
                
            # pd.set_option('display.max_columns', None)#显示所有列
            # pd.set_option('display.max_rows', None)#显示所有行

            df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
            # print(f"** {type(df)} **")
            # print((df))
            # dfm = pd.concat(df, ignore_index=True) ##dfm df_merge
            ##
            df['當月營收'] = pd.to_numeric(df['營業收入']['當月營收'], 'coerce')
            df = df[~df['營業收入']['當月營收'].isnull()]
            df = df[df['Unnamed: 0_level_0']['公司 代號'] != '合計']
            df = df[df['Unnamed: 0_level_0']['公司 代號'] != '全部國內上市公司合計']
            ##
            # dfm.append(df) # tw_revenue_analyze.py

            df = df.rename(columns={'公司 代號': 'code'})
            df = df.reset_index(drop=True)

            df.to_csv(f'tmp_tw_revenue_{year}_{str(imonth)}.csv', index=False)
        except:
            pass

    exit('EXC')
    # print(type(dfm))
    # print((dfm))
    
    # for tdfm in reversed(dfm):
    #     print(f"{tdfm}")
    # print(dfm[2].columns.get_level_values(1))
    # print(dfm[1].columns.get_level_values(1))
    # print(dfm[0].columns.get_level_values(1))
    # dfms = dfm[0].rename(columns={'公司 代號': 'code'})
    # dfms = dfms.reset_index(drop=True)
    # print(dfms)
    # print(dfms[2])
    # print(dfms['營業收入']['code'])
    # print(dfms.index)
    # print(dfms.columns)
    # print(dfms.columns.get_level_values(1))
    # print(dfms.loc['code'])
    # dfms.to_csv(f'tmp_tw_revenue_{year}_{str(month)}.csv', index=False)
    # for dd in dfms['Unnamed: 0_level_0']['code']:
    #     print(dd)
    
    ## ==
    if 'levels' in dir(df.columns):
        df.columns = df.columns.get_level_values(1)
        # print(f"** {df.columns} **")
    else:
        df = df[list(range(0,10))]
        column_index = df.index[(df[0] == '公司 代號')][0]
        df.columns = df.iloc[column_index]
        # print(f"** {df.columns} **")
    
    df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
    df = df[~df['當月營收'].isnull()]
    df = df[df['公司 代號'] != '合計']


year = int(sys.argv[1]) ## 明國西元年皆可
month = str(sys.argv[2]) ## 月份 不要補0

ar = analyze_report(year, month)