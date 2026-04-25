# AIoT 課程作業
這裡存放中興大學 AIoT 課程的所有作業。

## [HW2] 氣溫預報 Web App
這是一個整合氣象局 API、SQLite 資料庫與 Streamlit 視覺化介面的網頁應用程式。

**[🚀 線上展示連結 (Live Demo)](https://aiot-hw2-6swcqrqdqvwrfxibqedcsw.streamlit.app/)**

### 功能特點
- **數據自動化**：自動從 CWA API 獲取一週地區天氣預報。
- **資料持久化**：將氣溫數據存入 SQLite 資料庫，支持離線查詢。
- **互動式圖表**：使用 Streamlit 繪製最高與最低氣溫趨勢圖。
- **架構設計**：採用後端抓取 (ETL) 與前端呈現分離的架構。

### 如何執行
1. 安裝必要套件：`pip install -r HW2/requirements.txt`
2. 在 `HW2/` 資料夾下建立 `.env` 檔案並填入 `CWA_TOKEN=你的授權碼`
3. 執行資料抓取：`python HW2/fetch_and_store.py`
4. 啟動網頁：`streamlit run HW2/app.py`
