import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import datetime
from PIL import Image
import plotly.express as px


# 추후 배경 및 글자 색, 폰트 등 설정해야함
# https://www.youtube.com/watch?v=Mz12mlwzbVU


st.set_page_config(page_title='보이스 피싱')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title('보이스 피싱 📞')

# 데이터 불러오기
df = pd.read_csv('C:/Users/park/comp/vp_count.csv')


st.sidebar.header("금일 날짜 / 거주 지역:")
date = st.sidebar.selectbox(
    "금일 날짜를 선택해 주세요:",
    df['ymd'].unique()[365:]
)

area = st.sidebar.selectbox(
    "거주 지역을 선택해 주세요:",
    df['도시'].unique()
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
st.write('여기 정민 누나 부분이 들어갈거에요')





# -------차트 부분---------
# 월별 추이
last_year = df.loc[(df['DM_Y'] == preyear) & (df['도시'] == area)]
monthly_data = df.loc[(df['DM_Y'] == preyear) & (df['DM_M'] <= premonth) & (df['도시'] == area)]
monthly_data = monthly_data.groupby(['DM_Y','DM_M'])['신고횟수'].sum().reset_index()


df = px.data.gapminder()
# 작년 한해
fig1 = px.bar(
    last_year,
    x="DM_M",
    y="신고횟수",
)


# 올해 현재까지
fig2 = px.bar(
    monthly_data,
    x="DM_M",
    y="신고횟수",
)

tab1, tab2 = st.tabs(["작년 월별 신고 건수 추이", "올해 월별 신고 건수 추이"])
with tab1:
    # Use the Streamlit theme.
    # This is the default. So you can also omit the theme argument.
    st.plotly_chart(fig1, theme="streamlit")
with tab2:
    # Use the native Plotly theme.
    st.plotly_chart(fig2, theme='streamlit', use_container_width=True)




# 은솔누나 부분
map_info = Image.open('info.jpg')
st.image(map_info)
