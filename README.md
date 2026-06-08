# 每日 AI 資訊中心

繁體中文 Streamlit 應用，彙整四大新聞板塊並每日自動更新。

## 功能

- 🤖 **AI 新聞** — 依 AI 相關度與時間排序，附簡要重點摘要
- 🧵 **Threads 台灣** — 優先顯示 AI / 人工智慧 / LLM / Agent 相關話題
- 🧶 **Threads 香港** — 香港地區 Threads AI 熱門話題
- 🇭🇰 **香港 Google 新聞** — 香港本地頭條
- 🌍 **國際熱門話題** — 全球國際新聞

## 安裝與啟動

```bash
cd ai-daily-app
pip install -r requirements.txt
streamlit run app.py
```

## 每日自動更新

快取有效期為 **12 小時**，並依香港時間於 **08:00** 與 **18:00** 兩個時段更新。App 開啟時會自動判斷是否需要刷新。

也可設定 cron 配合排程背景更新：

```bash
0 8,18 * * * cd /Users/churchur/ai-daily-app && python3 update_cache.py
```

## 專案結構

```
ai-daily-app/
├── app.py              # Streamlit 主應用
├── cache.py            # 每日快取邏輯
├── update_cache.py     # 背景更新腳本
├── fetchers/           # RSS 新聞抓取
└── data/cache/         # 快取資料
```