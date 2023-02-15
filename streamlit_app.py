import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import datetime
from PIL import Image
import plotly.express as px
import requests
import numpy as np
import re
from collections import Counter
from konlpy.tag import Twitter
from konlpy.tag import Okt 
import os
import sys
import urllib.request



# 추후 배경 및 글자 색, 폰트 등 설정해야함
# https://www.youtube.com/watch?v=Mz12mlwzbVU


st.set_page_config(page_title='보이스 피싱')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    
# 로고 부분
logo = Image.open('logo.png')
st.image(logo)

st.title('보이스 피싱')

# 데이터 불러오기
# df = pd.read_csv('C:/Users/park/comp/vp_count.csv')
df = pd.read_csv('vp_count.csv')

st.sidebar.header("금일 날짜 / 거주 지역:")
date = st.sidebar.selectbox(
    "금일 날짜를 선택해 주세요:",
    df['ymd'].unique()[365:],index=250
)

area = st.sidebar.selectbox(
    "거주 지역을 선택해 주세요:",
    df['도시'].unique(), index=5
)

df_selection = df.query(
    "ymd == @date & 도시 ==@area"
)

# -----------첫번 째 열-----------

#오늘 신고 횟수
day_count = int(df_selection['신고횟수'].sum())

# 이번 달 신고 횟수
ye = pd.to_datetime(date).year
mon = pd.to_datetime(date).month
day = pd.to_datetime(date).day
month_count = df.loc[(df['DM_Y'] == ye) & (df['DM_M'] == mon) & (df['DM_D'] <= day)  &(df['도시'] == area)]['신고횟수'].sum()

# 전날 신고 횟수
pre = pd.to_datetime(date) - datetime.timedelta(days=1)
pre_y = pd.to_datetime(pre).year
pre_m = pd.to_datetime(pre).month
pre_d = pd.to_datetime(pre).day
preday_count = df.loc[(df['DM_Y'] == pre_y) & (df['DM_M'] == pre_m) & (df['DM_D'] == pre_d) & (df['도시'] == area)]['신고횟수'].sum()


# 전달 신고 횟수
if mon == 1: # 만약 오늘이 1월일 경우, 전년도 12월로 바뀜
    premonth = 12
    preyear = ye - 1
else: # 기본적인 전월
    premonth = mon-1
    preyear = ye

premonth_count = df.loc[(df['DM_Y'] == preyear) & (df['DM_M'] == premonth) & (df['도시'] == area)]['신고횟수'].sum()

# 신고 건수 차이
month_diff = int(month_count - premonth_count) # 오늘 - 전날 신고 건수
day_diff = int(day_count - preday_count) # 이번달 - 전달 신고 건수


# 네모 박스
col1, col2 = st.columns(2)
col1.metric("이번달", f'{month_count}건', month_diff) # 이번달, 이번달 신고 건수, 이번달 - 저번달
col2.metric("오늘", f'{day_count}건', day_diff) # # 오늘, 오늘 신고 건수, 오늘 - 어제




# --------트렌드----------
###### api사용해서 불러오기 

client_id = "7BluQlzfnBbWg8ALRkpq"
client_secret = "ZTCPVEwdLc"
url = 'https://openapi.naver.com/v1/search/news.json'



# display_num : 한 번에 표시할 검색 결과 개수(기본값: 10, 최댓값: 100)
def Keword( key, display_num):
      # keyword = key
      headers = { 'X-Naver-Client-Id': client_id
                , 'X-Naver-Client-Secret': client_secret}
      params = {'query': key
                , 'display':display_num
                ,'sort': 'sim' }

      r = requests.get(url, params = params, headers = headers).json()['items']

      return r 


## 데이터프레임에 나눠담기
def info(places):
    PubDate = []
    Title = []
    Link = [] 
    Description = []

    for place in places:

        PubDate.append(place['pubDate'])
        Title.append(place['title'])
        Link.append(place['originallink'])      
        Description.append(place['description'])
         

    ar = np.array([PubDate, Title, Link, Description ]).T
    dtf = pd.DataFrame(ar, columns=['PubDate', 'Title', 'Link', 'Description' ])

    return dtf


####가져오기 

search = Keword('신종보이스피싱수법',100)
news = info(search) 



# 기본 정제 
def basic_clear(text):
    for i in range(len(text)) : 
        text[i] = text[i].replace('<b>', '')
        text[i] = text[i].replace('</b>', '')
        text[i] = text[i].replace('&apos;', '') 
        text[i] = text[i].replace('&quot;', '') 
    return text

basic_clear(news['Title'])
basic_clear(news['Description'])


## 중복 타이틀 제거
for i in range(99):
        if news['Title'].iloc[i][:8] == news['Title'].iloc[i+1][:8]:
             news['Title'].iloc[i] = np.NaN
news.dropna(inplace=True)
news.info()

import datetime


# 날짜형으로 형변환

news['PubDate'] = pd.to_datetime(news['PubDate'], format='%a, %d %b %Y  %H:%M:%S', exact=False) # 수정완료!

# news['PubDate'] = 
news['PubDate'] = news['PubDate'].dt.strftime('%m.%d') # 수정완료!



a = news[['PubDate','Title','Link']].head(5)

st.write('관련 뉴스')
for i in range(len(a['Title'])):
    txt='{date}    [{txt}]({link})'.format(date =  a['PubDate'][i], txt = a['Title'][i], link = a['Link'][i])
    st.write(txt) 
    
    

# -------차트 부분---------
# 전체 일별 지역별 신고 건수
all_data = df.groupby(['ymd', '도시'])['신고횟수'].sum().reset_index()
recent_days = all_data.loc[(all_data['ymd'] < date) & (all_data['도시'] == area)][-7:] # 최근 7일
recent_months = all_data.loc[(all_data['ymd'] < date) & (all_data['도시'] == area)][-30:] # 최근 30일
recent_years = all_data.loc[(all_data['ymd'] < date) & (all_data['도시'] == area)][-365:] # 최근 1년


df = px.data.gapminder()

st.subheader('신고건수 추이')
# 최근 7일
fig1 = px.bar(
    recent_days,
    x="ymd",
    y="신고횟수", text_auto='.2s'
)

fig1.update_layout(xaxis_title=None)
fig1.update_layout(yaxis_title='신고건수')

# 최근 30일
fig2 = px.line(
    recent_months,
    x="ymd",
    y="신고횟수"
)
fig2.update_layout(xaxis_title=None)
fig2.update_layout(yaxis_title='신고건수')

# 최근 1년
fig3 = px.line(
    recent_years,
    x="ymd",
    y="신고횟수",
)
fig3.update_layout(xaxis_title=None)
fig3.update_layout(yaxis_title='신고건수')



tab1, tab2, tab3 = st.tabs(["최근7일", "최근30일", "최근1년"])
with tab1:
    # Use the Streamlit theme.
    # This is the default. So you can also omit the theme argument.
    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
with tab2:
    # Use the native Plotly theme.
    st.plotly_chart(fig2, theme='streamlit', use_container_width=True)

with tab3:
    # Use the native Plotly theme.
    st.plotly_chart(fig3, theme='streamlit', use_container_width=True)




# 이미지 부분
map_info = Image.open('info.jpg')
st.image(map_info)
