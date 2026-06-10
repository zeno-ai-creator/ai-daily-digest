# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-TW/).

## [1.3.1] - 2026-06-10

### Added
- Apple 相關來源權重強化：
  - 在 `ai_news`（AI 新聞）、Threads 以及香港/國際板塊的 Google News RSS 查詢中加入 `Apple WWDC OR "Siri AI" OR "Apple Intelligence" OR WWDC2026` 等關鍵字。
  - 新增 Apple 專用 search feed 到 `hk_news` 與 `international`，確保本地討論與全球熱門 Apple AI 內容能被抓取。
- `fetchers/scoring.py`：`AI_KEYWORDS` 新增高權重項目（WWDC / Apple Intelligence = 8、Siri AI = 7、Siri/Apple/蘋果 = 5~6），大幅提升 Apple 內容在 AI 新聞板塊的排序優先度。
- `fetchers/daily_analysis.py`：
  - `INTERNATIONAL_KEYWORDS` 加入 Apple 權重，影響每日重點分析的選取與優先排序。
  - `THEME_RULES` 新增 "apple" 主題，提供專屬的 importance 與 regional 說明文字。
  - `GIANT_RULES` 新增 "apple" 巨頭規則，讓 Apple 相關動態可出現在「AI Agent 與巨頭動態」卡片區（藍色樣式）。
- 新增 GitHub Actions workflow (`.github/workflows/update-cache.yml`)，支援 schedule 與 `workflow_dispatch` 手動觸發。

### Changed
- 強化「立即更新」按鈕的強制清除快取功能（`cache.py`）：
  - `force_refresh=True` 時會先刪除 `data/cache/daily_news.json`，再執行完整刷新，保證拿到最新資料（含新 Apple 權重）。
  - 忽略原有 TTL 與 slot 檢查。
- `update_cache.py` 與 cron 範例改用通用路徑說明。
- README 全面更新：新增 Apple 功能說明、PWA 安裝指引、立即更新行為描述、修正板塊數量、連結 CHANGELOG。

### Fixed
- 重點分析 HTML 渲染問題：
  - app.py 內**所有** `st.markdown(...)` 呼叫皆強制加上 `unsafe_allow_html=True`。
  - `render_highlight` 與 `render_agent_giant_item` 的 `analysis-label`、`analysis-text`、`read-source` 等自訂 HTML 結構現在正確渲染，不再出現 raw div。
  - 同時保留 emoji（🌐 ⚡ 🇭🇰🇹🇼）與點擊連結的正常顯示。
- 修正 README 中「四大板塊」與實際 5 個板塊的不一致問題。
- 移除 cron 範例中硬編碼的本地路徑。

### Technical
- 所有修改檔案通過 `py_compile` 語法檢查。
- 執行 `python3 update_cache.py --verbose` 產生最新快取（72 則文章，6 條重點分析，4 則巨頭動態），驗證新 Apple 邏輯已生效。

## [1.3.0] - 2026-06-10 (Apple Initial)

- 初始 Apple WWDC / Siri AI / Apple Intelligence 權重與快取強制清除 + HTML 渲染修復（標籤 v1.3-apple-weights）。

## [1.2.x] - 之前版本

- 基礎每日 AI 資訊中心功能（AI 新聞、Threads 台港、香港/國際頭條、重點分析卡片、PWA 支援、自訂追蹤巨頭等）。

[1.3.1]: https://github.com/zeno-ai-creator/ai-daily-digest/compare/v1.3-apple-weights...v1.3.1
[1.3.0]: https://github.com/zeno-ai-creator/ai-daily-digest/releases/tag/v1.3-apple-weights
