import os
import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

@st.cache_data
def load_data(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

st.set_page_config(page_title="서울 공공자전거 분석", layout="wide")
st.title("🚲 서울 공공자전거 이용 분석")

tab1, tab2, tab3 = st.tabs(["시간대별 이용 패턴", "사용자 특성 분석", "인기 대여소 순위"])

# 1. 시간대별 이용 패턴
with tab1:
    st.subheader("⏰ 시간대별 이용 패턴")
    df_hourly = load_data("SELECT * FROM fct_hourly_usage ORDER BY rental_hour")

    # time_slot 컬럼 한글 순서 지정
    slot_order = ['출근 시간', '점심 시간', '퇴근 시간', 'OTHER']
    df_hourly['TIME_SLOT'] = pd.Categorical(df_hourly['TIME_SLOT'], categories=slot_order)

    fig = px.bar(df_hourly, x="RENTAL_HOUR", y="TOTAL_USAGE",
                 color="TIME_SLOT",
                 color_discrete_map={
                     '출근 시간': '#FF6B6B',
                     '점심 시간': '#FFD93D',
                     '퇴근 시간': '#6BCB77',
                     'OTHER': '#ADB5BD'
                 },
                 labels={"RENTAL_HOUR": "시간대", "TOTAL_USAGE": "총 이용건수", "TIME_SLOT": "시간 구분"},
                 title="시간대별 이용건수")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.line(df_hourly, x="RENTAL_HOUR", y="AVG_DISTANCE",
                       markers=True,
                       title="시간대별 평균 이동거리(M)",
                       labels={"RENTAL_HOUR": "시간대", "AVG_DISTANCE": "평균 이동거리(M)"})
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = px.line(df_hourly, x="RENTAL_HOUR", y="AVG_DURATION",
                       markers=True,
                       title="시간대별 평균 이용시간(분)",
                       labels={"RENTAL_HOUR": "시간대", "AVG_DURATION": "평균 이용시간(분)"})
        st.plotly_chart(fig3, use_container_width=True)

# 2. 사용자 특성 분석

# 성별 색상 통일
gender_color = {
    'M': '#B9E0FD',
    'F': "#FFCC80"
}

with tab2:
    st.subheader("👥 성별/연령대별 이용 패턴")
    df_user = load_data("SELECT * FROM fct_user_profile")

    col1, col2 = st.columns(2)
    with col1:
        df_gender = df_user.groupby("GENDER")["TOTAL_USAGE"].sum().reset_index()
        fig4 = px.pie(df_gender, names="GENDER", values="TOTAL_USAGE",
                      color="GENDER",
                    color_discrete_map=gender_color,
                      title="성별 이용 비율")
        st.plotly_chart(fig4, use_container_width=True)
    with col2:
        fig5 = px.bar(df_user, x="AGE_GROUP", y="TOTAL_USAGE",
                      color="GENDER",
                      color_discrete_map=gender_color,
                      title="연령대별 이용건수",
                      labels={"AGE_GROUP": "연령대", "TOTAL_USAGE": "총 이용건수"})
        st.plotly_chart(fig5, use_container_width=True)

    fig6 = px.bar(df_user, x="AGE_GROUP", y="AVG_DISTANCE",
              color="GENDER",
              color_discrete_map=gender_color,
              barmode="group",
              title="연령대별 평균 이동거리",
              labels={"AGE_GROUP": "연령대", "AVG_DISTANCE": "평균 이동거리(M)", "GENDER": "성별"})
    st.plotly_chart(fig6, use_container_width=True)

# 3. 인기 대여소 순위
with tab3:
    st.subheader("📍 인기 대여소 TOP 20")
    df_station = load_data("""
        SELECT station_name, total_usage, avg_distance, total_carbon_amount, usage_rank
        FROM fct_station_ranking
        ORDER BY usage_rank
        LIMIT 20
    """)

    fig7 = px.bar(df_station, x="TOTAL_USAGE", y="STATION_NAME",
                  orientation="h",
                  title="이용건수 TOP 20 대여소",
                  labels={"TOTAL_USAGE": "총 이용건수", "STATION_NAME": "대여소명"},
                  color="TOTAL_USAGE",
                  color_continuous_scale="Blues")
    fig7.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("📊 TOP 20 대여소 상세 데이터")
    st.dataframe(df_station, use_container_width=True)