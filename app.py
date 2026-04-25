import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

import os
from fetch_and_store import fetch_weather_data, process_and_store_data

# 設定網頁標題
st.set_page_config(page_title="氣溫預報 Web App", layout="wide")

# 自動初始化資料庫 (如果不存在或表單遺失)
def initialize_db():
    if not CWA_TOKEN:
        st.error("❌ 找不到 CWA_TOKEN！請在 Streamlit Cloud 的 Secrets 中設定。")
        return

    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TemperatureForecasts'")
        table_exists = cursor.fetchone()
        conn.close()
        
        if not table_exists:
            st.warning("⚠️ 資料庫表格遺失，嘗試初始化...")
            data = fetch_weather_data()
            if data:
                process_and_store_data(data)
                st.success("✅ 資料庫初始化成功！")
                st.rerun() # 重新整理頁面以讀取新資料
            else:
                st.error("❌ 無法從 API 獲取資料，請檢查 Token 是否正確。")
    except Exception as e:
        st.error(f"❌ 資料庫初始化過程發生錯誤: {e}")

initialize_db()

st.title("Temperature Forecast Web App")

def get_connection():
    return sqlite3.connect("data.db")

def load_regions():
    conn = get_connection()
    df = pd.read_sql_query("SELECT DISTINCT regionName FROM TemperatureForecasts", conn)
    conn.close()
    return df['regionName'].tolist()

def load_data(region_name):
    conn = get_connection()
    query = f"SELECT dataDate, minT, maxT FROM TemperatureForecasts WHERE regionName = '{region_name}' ORDER BY dataDate"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 側邊欄或上方選擇框
regions = load_regions()
if regions:
    selected_region = st.selectbox("Select a Region", regions)

    if selected_region:
        st.subheader(f"Temperature Trends for {selected_region}")
        
        # 載入選定地區的資料
        df = load_data(selected_region)
        
        if not df.empty:
            # 轉換資料格式以方便繪圖 (Melt dataframe)
            df_melted = df.melt(id_vars=['dataDate'], value_vars=['minT', 'maxT'], 
                                var_name='Temperature Type', value_name='Temperature (℃)')
            
            # 使用 Altair 繪製折線圖 (比 st.line_chart 更美觀且可控)
            chart = alt.Chart(df_melted).mark_line(point=True).encode(
                x=alt.X('dataDate:T', title='Date'),
                y=alt.Y('Temperature (℃):Q', title='Temperature (℃)', scale=alt.Scale(zero=False)),
                color='Temperature Type:N'
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
            
            # 顯示表格
            st.subheader(f"Temperature Data for {selected_region}")
            st.table(df)
        else:
            st.warning("該地區尚無資料。")
else:
    st.error("資料庫中沒有資料，請先執行 fetch_and_store.py 抓取資料！")

# 頁尾資訊
st.markdown("---")
st.caption("資料來源：交通部中央氣象署 (CWA)")
