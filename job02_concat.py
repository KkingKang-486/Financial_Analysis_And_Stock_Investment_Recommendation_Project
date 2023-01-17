import pandas as pd
import glob
import datetime

data_path = glob.glob('./crawling_data/*.csv')
print(data_path)
df = pd.DataFrame()
for path in data_path:
    df_temp = pd.read_csv(path)
    df = pd.concat([df,df_temp], ignore_index=True)
df.dropna(inplace=True)                  # 중복제거 추가
df.reset_index(inplace=True, drop=True)

df.dropna(inplace = True)
df.reset_index(inplace = True, drop = True)
print(df.head())

df.info()
df.to_csv('./crawling_data/news_crawling_data_기업,종목분석_{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index = False)