import os
import requests
import sqlite3
from dotenv import load_dotenv

# 加載環境變數 (.env)
load_dotenv()
CWA_TOKEN = os.getenv("CWA_TOKEN")

# 如果在 Streamlit 環境下且沒找到環境變數，嘗試讀取 st.secrets
if not CWA_TOKEN:
    try:
        import streamlit as st
        CWA_TOKEN = st.secrets["CWA_TOKEN"]
    except:
        pass

def fetch_weather_data():
    """HW2-1: 獲取天氣預報資料 (使用檔案資源 API)"""
    print("正在從 CWA 檔案資源 API 獲取資料 (F-A0010-001)...")
    # F-A0010-001 必須使用 fileapi 路徑
    url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization={CWA_TOKEN}&downloadType=WEB&format=JSON"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"獲取資料失敗: {e}")
        return None

def process_and_store_data(data):
    """HW2-2 & HW2-3: 分析資料並儲存至 SQLite3"""
    if not data:
        return

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # 建立表格
    cursor.execute("DROP TABLE IF EXISTS TemperatureForecasts")
    cursor.execute("""
        CREATE TABLE TemperatureForecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT,
            dataDate TEXT,
            minT INTEGER,
            maxT INTEGER
        )
    """)

    print("正在解析資料並儲存至資料庫...")
    
    try:
        # 根據觀察到的 structure.json 進行路徑導航
        locations = data['cwaopendata']['resources']['resource']['data']['agrWeatherForecasts']['weatherForecasts']['location']
        
        for loc in locations:
            region_name = loc['locationName']
            weather_elements = loc['weatherElements']
            
            # 提取 MaxT 和 MinT
            max_t_list = weather_elements['MaxT']['daily']
            min_t_list = weather_elements['MinT']['daily']
            
            # 建立日期索引的字典以便合併
            daily_data = {} # { "2024-04-13": {"min": 17, "max": 22} }
            
            for item in max_t_list:
                date = item['dataDate']
                daily_data[date] = daily_data.get(date, {})
                daily_data[date]['max'] = int(item['temperature'])
                
            for item in min_t_list:
                date = item['dataDate']
                daily_data[date] = daily_data.get(date, {})
                daily_data[date]['min'] = int(item['temperature'])

            # 寫入資料庫
            for date, temps in daily_data.items():
                if 'min' in temps and 'max' in temps:
                    cursor.execute("""
                        INSERT INTO TemperatureForecasts (regionName, dataDate, minT, maxT)
                        VALUES (?, ?, ?, ?)
                    """, (region_name, date, temps['min'], temps['max']))

        conn.commit()
        print("資料儲存成功！")
        
        # 驗證查詢
        print("\n--- 資料庫測試查詢 ---")
        cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts")
        regions = [r[0] for r in cursor.fetchall()]
        print(f"已成功存入 {len(regions)} 個地區: {', '.join(regions)}")

    except Exception as e:
        print(f"處理資料時發生錯誤: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    weather_data = fetch_weather_data()
    process_and_store_data(weather_data)
