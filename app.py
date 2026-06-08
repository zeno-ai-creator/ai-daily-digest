from __future__ import annotations

import html
import re

import streamlit as st

from cache import (
    format_updated_at,
    get_current_hk_time_label,
    get_daily_data,
    get_next_refresh_datetime,
    next_refresh_label,
)
from fetchers.daily_analysis import generate_daily_analysis

st.set_page_config(
    page_title="每日 AI 資訊中心",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ 主題與樣式 ============
DARK_CSS = """
<style>
:root {
    --card-bg: #1A1F2E;
    --card-border: #2D3748;
    --card-hover-border: #3B82F6;
    --text-primary: #E2E8F0;
    --text-secondary: #9CA3AF;
    --text-body: #CBD5E1;
    --accent-blue: #93C5FD;
    --badge-blue-bg: #1E3A5F;
    --badge-blue-text: #93C5FD;
    --gradient-blue: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
    --gradient-green: linear-gradient(135deg, #0F172A 0%, #14532D 100%);
}
.main-header { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem; color: #E2E8F0; }
.sub-header { color: #9CA3AF; font-size: 1rem; margin-bottom: 1.5rem; }
.section-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.section-card:hover {
    border-color: var(--card-hover-border);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.25), 0 4px 6px -4px rgba(0, 0, 0, 0.2);
    transform: translateY(-3px);
}
.article-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.35rem; line-height: 1.45; color: #E2E8F0; }
.article-meta { color: #9CA3AF; font-size: 0.85rem; margin-bottom: 0.45rem; }
.article-summary { color: #CBD5E1; font-size: 0.92rem; line-height: 1.5; margin-top: 0.2rem; }
.analysis-label { color: #93C5FD; font-size: 0.82rem; font-weight: 600; margin-top: 0.55rem; margin-bottom: 0.15rem; }
.analysis-text { color: #CBD5E1; font-size: 0.92rem; line-height: 1.55; margin-bottom: 0.2rem; }
.ai-badge {
    display: inline-block; background: #1E3A5F; color: #93C5FD;
    font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 999px; margin-left: 0.4rem; vertical-align: middle;
}
.subsection-title { font-size: 1.2rem; font-weight: 700; margin: 1.6rem 0 0.6rem 0; color: #E2E8F0; }
.agent-card-blue {
    background: var(--gradient-blue); border: 1px solid #3B82F6; border-radius: 12px;
    padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.agent-card-blue:hover {
    border-color: #60A5FA;
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.35), 0 4px 6px -4px rgba(59, 130, 246, 0.2);
    transform: translateY(-3px);
}
.agent-card-green {
    background: var(--gradient-green); border: 1px solid #22C55E; border-radius: 12px;
    padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.agent-card-green:hover {
    border-color: #4ADE80;
    box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.35), 0 4px 6px -4px rgba(34, 197, 94, 0.2);
    transform: translateY(-3px);
}
.giant-badge-blue { display: inline-block; background: #1D4ED8; color: #DBEAFE; font-size: 0.75rem; padding: 0.15rem 0.55rem; border-radius: 999px; margin-left: 0.4rem; vertical-align: middle; }
.giant-badge-green { display: inline-block; background: #15803D; color: #DCFCE7; font-size: 0.75rem; padding: 0.15rem 0.55rem; border-radius: 999px; margin-left: 0.4rem; vertical-align: middle; }
.agent-label-blue { color: #93C5FD; }
.agent-label-green { color: #86EFAC; }
.search-result-banner { background: #1E2937; border: 1px solid #334155; border-radius: 8px; padding: 0.5rem 0.9rem; margin-bottom: 0.8rem; font-size: 0.9rem; color: #CBD5E1; }
.tracked-chip { display: inline-block; background: #1D4ED8; color: #DBEAFE; font-size: 0.7rem; padding: 0.1rem 0.45rem; border-radius: 999px; margin-left: 0.35rem; }
</style>
"""

LIGHT_CSS = """
<style>
:root {
    --card-bg: #FFFFFF;
    --card-border: #E2E8F0;
    --card-hover-border: #3B82F6;
    --text-primary: #1E293B;
    --text-secondary: #64748B;
    --text-body: #334155;
    --accent-blue: #1E40AF;
    --badge-blue-bg: #DBEAFE;
    --badge-blue-text: #1E40AF;
    --gradient-blue: linear-gradient(135deg, #F1F5F9 0%, #E0F2FE 100%);
    --gradient-green: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
}
.main-header { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem; color: #0F172A; }
.sub-header { color: #64748B; font-size: 1rem; margin-bottom: 1.5rem; }
.section-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.section-card:hover {
    border-color: var(--card-hover-border);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    transform: translateY(-3px);
}
.article-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.35rem; line-height: 1.45; color: #0F172A; }
.article-meta { color: #64748B; font-size: 0.85rem; margin-bottom: 0.45rem; }
.article-summary { color: #334155; font-size: 0.92rem; line-height: 1.5; margin-top: 0.2rem; }
.analysis-label { color: #1E40AF; font-size: 0.82rem; font-weight: 600; margin-top: 0.55rem; margin-bottom: 0.15rem; }
.analysis-text { color: #334155; font-size: 0.92rem; line-height: 1.55; margin-bottom: 0.2rem; }
.ai-badge {
    display: inline-block; background: #DBEAFE; color: #1E40AF;
    font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 999px; margin-left: 0.4rem; vertical-align: middle;
}
.subsection-title { font-size: 1.2rem; font-weight: 700; margin: 1.6rem 0 0.6rem 0; color: #0F172A; }
.agent-card-blue {
    background: var(--gradient-blue); border: 1px solid #3B82F6; border-radius: 12px;
    padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.agent-card-blue:hover {
    border-color: #2563EB;
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2), 0 4px 6px -4px rgba(59, 130, 246, 0.15);
    transform: translateY(-3px);
}
.agent-card-green {
    background: var(--gradient-green); border: 1px solid #16A34A; border-radius: 12px;
    padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.agent-card-green:hover {
    border-color: #15803D;
    box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.2), 0 4px 6px -4px rgba(34, 197, 94, 0.15);
    transform: translateY(-3px);
}
.giant-badge-blue { display: inline-block; background: #1D4ED8; color: #DBEAFE; font-size: 0.75rem; padding: 0.15rem 0.55rem; border-radius: 999px; margin-left: 0.4rem; vertical-align: middle; }
.giant-badge-green { display: inline-block; background: #15803D; color: #DCFCE7; font-size: 0.75rem; padding: 0.15rem 0.55rem; border-radius: 999px; margin-left: 0.4rem; vertical-align: middle; }
.agent-label-blue { color: #1E40AF; }
.agent-label-green { color: #15803D; }
.search-result-banner { background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.5rem 0.9rem; margin-bottom: 0.8rem; font-size: 0.9rem; color: #334155; }
.tracked-chip { display: inline-block; background: #1D4ED8; color: #DBEAFE; font-size: 0.7rem; padding: 0.1rem 0.45rem; border-radius: 999px; margin-left: 0.35rem; }
</style>
"""


def inject_theme_css() -> None:
    """根據 session_state 注入對應主題 CSS（深色預設）。"""
    is_dark = st.session_state.get("is_dark", True)
    st.markdown(DARK_CSS if is_dark else LIGHT_CSS, unsafe_allow_html=True)


def toggle_theme() -> None:
    """切換深/淺色模式並重新執行。"""
    current = st.session_state.get("is_dark", True)
    st.session_state["is_dark"] = not current
    st.rerun()


# ============ 巨頭追蹤設定 ============
GIANT_OPTIONS: list[tuple[str, str]] = [
    ("xai", "Elon Musk / xAI"),
    ("nvidia", "黃仁勳 / NVIDIA"),
    ("openai", "OpenAI"),
    ("google", "Google"),
    ("anthropic", "Anthropic"),
    ("meta", "Meta"),
    ("microsoft", "Microsoft"),
]


def get_tracked_giant_labels() -> list[str]:
    """取得使用者目前勾選的巨頭顯示名稱列表。"""
    selected_keys: list[str] = st.session_state.get("tracked_giant_keys", ["xai", "nvidia", "openai", "google", "anthropic"])
    label_map = {k: label for k, label in GIANT_OPTIONS}
    return [label_map.get(k, k) for k in selected_keys if k in label_map]


def get_tracked_giant_keys() -> list[str]:
    return st.session_state.get("tracked_giant_keys", ["xai", "nvidia", "openai", "google", "anthropic"])


def matches_tracked(text: str, keys: list[str] | None = None) -> bool:
    """判斷文字是否命中任一追蹤巨頭關鍵字。"""
    if not text:
        return False
    keys = keys or get_tracked_giant_keys()
    lowered = text.lower()
    for k in keys:
        # 直接比對 label 片段或 key
        for kk, ll in GIANT_OPTIONS:
            if kk == k:
                if kk in lowered or any(p in lowered for p in ll.lower().split() if len(p) > 2):
                    return True
    return False




def get_analysis_payload(data: dict) -> dict:
    analysis = data.get("daily_analysis")
    if analysis and analysis.get("highlights") and analysis.get("agent_giants"):
        return analysis
    return generate_daily_analysis(data.get("sections", []))


def _highlight_match(text: str, query: str) -> str:
    """簡單將搜尋關鍵字以底線標註（純文字安全）。"""
    if not query or not text:
        return html.escape(text)
    try:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(lambda m: f"<u style='text-decoration-color:#3B82F6;text-underline-offset:3px;'>{html.escape(m.group(0))}</u>", html.escape(text))
    except Exception:
        return html.escape(text)


def render_agent_giant_item(item: dict, index: int, *, search_query: str = "", tracked_keys: list[str] | None = None) -> None:
    event = item.get("event", "")
    importance = item.get("importance", "")
    regional = item.get("regional", "")
    giant = item.get("giant", "")
    source = item.get("source", "")
    link = item.get("link", "#")
    card_style = item.get("card_style", "blue")

    card_class = "agent-card-blue" if card_style == "blue" else "agent-card-green"
    badge_class = "giant-badge-blue" if card_style == "blue" else "giant-badge-green"
    label_class = "agent-label-blue" if card_style == "blue" else "agent-label-green"
    meta = f"參考來源：{source}" if source else "參考來源：新聞彙整"

    # 追蹤巨頭晶片
    tracked_chip = ""
    if tracked_keys and matches_tracked(f"{giant} {event}", tracked_keys):
        tracked_chip = '<span class="tracked-chip">⭐ 追蹤</span>'

    event_html = _highlight_match(event, search_query) if search_query else html.escape(event)

    st.markdown(
        f"""
        <div class="{card_class}">
            <div class="article-title">
                {index}. {event_html}
                <span class="{badge_class}">{html.escape(giant)}</span>
                {tracked_chip}
            </div>
            <div class="article-meta">
                <a href="{html.escape(link, quote=True)}" target="_blank" style="color: var(--text-secondary); text-decoration: none;">
                    {html.escape(meta)}
                </a>
            </div>
            <div class="analysis-label {label_class}">🌐 國際重點</div>
            <div class="analysis-text">{event_html}</div>
            <div class="analysis-label {label_class}">⚡ 重要性（全球影響）</div>
            <div class="analysis-text">{html.escape(importance)}</div>
            <div class="analysis-label {label_class}">🇭🇰🇹🇼 對香港／台灣影響</div>
            <div class="analysis-text">{html.escape(regional)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_highlight(highlight: dict, index: int, *, search_query: str = "", tracked_keys: list[str] | None = None) -> None:
    event = highlight.get("event", "")
    importance = highlight.get("importance", "")
    regional = highlight.get("regional", "")
    source = highlight.get("source", "")
    link = highlight.get("link", "#")

    meta = f"參考來源：{source}" if source else "參考來源：新聞彙整"

    tracked_chip = ""
    if tracked_keys and matches_tracked(f"{event} {importance} {regional}", tracked_keys):
        tracked_chip = '<span class="tracked-chip">⭐ 追蹤</span>'

    event_html = _highlight_match(event, search_query) if search_query else html.escape(event)

    st.markdown(
        f"""
        <div class="section-card">
            <div class="article-title">
                {index}. {event_html}
                {tracked_chip}
            </div>
            <div class="article-meta">
                <a href="{html.escape(link, quote=True)}" target="_blank" style="color: var(--text-secondary); text-decoration: none;">
                    {html.escape(meta)}
                </a>
            </div>
            <div class="analysis-label">🌐 國際核心事件／趨勢</div>
            <div class="analysis-text">{event_html}</div>
            <div class="analysis-label">⚡ 為什麼重要（全球影響）</div>
            <div class="analysis-text">{html.escape(importance)}</div>
            <div class="analysis-label">🇭🇰🇹🇼 對香港／台灣的可能影響或機會</div>
            <div class="analysis-text">{html.escape(regional)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_article(article: dict, *, show_ai_summary: bool = False, search_query: str = "") -> None:
    title = article.get("title", "無標題")
    link = article.get("link", "#")
    summary = article.get("summary", "")
    ai_summary = article.get("ai_summary", "")
    published = article.get("published") or ""
    source = article.get("source", "")
    ai_score = article.get("ai_score")

    meta_parts = [part for part in [source, published] if part]
    meta = " · ".join(meta_parts) if meta_parts else "來源未知"

    badge = ""
    if ai_score and ai_score >= 8:
        badge = f'<span class="ai-badge">AI 相關度 {ai_score}</span>'

    title_html = _highlight_match(title, search_query) if search_query else html.escape(title)

    summary_html = ""
    if show_ai_summary and ai_summary:
        s = _highlight_match(ai_summary, search_query) if search_query else html.escape(ai_summary)
        summary_html = f'<div class="article-summary">{s}</div>'
    elif summary:
        base = summary[:180] + ("..." if len(summary) > 180 else "")
        s = _highlight_match(base, search_query) if search_query else html.escape(base)
        summary_html = f'<div class="article-summary">{s}</div>'

    st.markdown(
        f"""
        <div class="section-card">
            <div class="article-title">
                <a href="{html.escape(link, quote=True)}" target="_blank" style="color: var(--text-primary); text-decoration: none;">
                    {title_html}
                </a>
                {badge}
            </div>
            <div class="article-meta">{html.escape(meta)}</div>
            {summary_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _filter_by_query(items: list[dict], query: str, text_keys: list[str]) -> list[dict]:
    """依查詢字串過濾（標題/事件 + 摘要/說明）。"""
    if not query:
        return items
    q = query.strip().lower()
    if not q:
        return items
    out = []
    for it in items:
        hay = " ".join(str(it.get(k, "")) for k in text_keys).lower()
        if q in hay:
            out.append(it)
    return out


def _prioritize_tracked(items: list[dict], tracked_keys: list[str], text_getter) -> list[dict]:
    """將命中追蹤巨頭的項目排在前面（其餘保持相對順序）。"""
    if not tracked_keys or not items:
        return items

    def score(item: dict) -> int:
        text = text_getter(item)
        return 1 if matches_tracked(text, tracked_keys) else 0

    # 穩定排序：score 高的在前
    return sorted(items, key=score, reverse=True)


def main() -> None:
    # 先注入主題 CSS（必須在其他 st 元素之前）
    inject_theme_css()

    # 先計算共用狀態（避免 scope 問題）
    current_hk = get_current_hk_time_label()
    next_dt = get_next_refresh_datetime()
    next_label = next_dt.strftime("%Y年%m月%d日 %H:%M")
    initial_search = st.session_state.get("global_search", "")

    # ========== 側邊欄 ==========
    with st.sidebar:
        st.title("📰 每日資訊")

        # 主題切換
        is_dark = st.session_state.get("is_dark", True)
        theme_label = "☀️ 切換淺色模式" if is_dark else "🌙 切換深色模式"
        if st.button(theme_label, use_container_width=True, key="theme_toggle"):
            toggle_theme()

        st.markdown("---")

        # 全域搜尋（側邊欄也放一個，頂部也會有）
        search_query = st.text_input(
            "🔍 全域搜尋（標題 / 摘要）",
            value=initial_search,
            key="global_search",
            placeholder="輸入關鍵字過濾新聞...",
        ).strip()

        st.markdown("---")

        # 自訂追蹤巨頭
        st.markdown("**🎯 自訂追蹤巨頭**")
        st.caption("勾選後將在「每日重點分析」與「AI Agent 與巨頭動態」優先顯示相關內容")

        current_keys = st.session_state.get("tracked_giant_keys", ["xai", "nvidia", "openai", "google", "anthropic"])
        new_keys: list[str] = []
        for key, label in GIANT_OPTIONS:
            checked = key in current_keys
            if st.checkbox(label, value=checked, key=f"giant_{key}"):
                new_keys.append(key)
        if new_keys != current_keys:
            st.session_state["tracked_giant_keys"] = new_keys
            # 不直接 rerun，避免輸入框干擾；下次互動會反映

        tracked_labels = get_tracked_giant_labels()
        if tracked_labels:
            st.caption("目前優先：" + "、".join(tracked_labels))

        st.markdown("---")

        # 六大板塊導覽
        st.markdown("**六大板塊**")
        st.markdown("- 📊 每日重點分析")
        st.markdown("- 🤖 AI 新聞（高相關排序 + 摘要）")
        st.markdown("- 🧵 Threads 台灣")
        st.markdown("- 🧶 Threads 香港")
        st.markdown("- 🇭🇰 香港 Google 新聞")
        st.markdown("- 🌍 國際熱門話題")

        st.markdown("---")

        # 更新狀態與控制
        st.markdown("**⏰ 更新狀態**")
        st.caption(f"目前香港時間：{current_hk}")
        st.caption(f"下次更新時間：{next_label}")
        st.caption("快取有效期 12 小時，香港時間每日 08:00 與 18:00 自動刷新。")

        force_refresh = st.button("🔄 立即更新", use_container_width=True)

        st.markdown("---")

        # 背景自動更新提示（Streamlit Cloud 相容）
        with st.expander("🔄 背景自動更新設定提示", expanded=False):
            st.markdown(
                """
                **Streamlit Community Cloud 限制**：無持久背景任務。

                推薦作法：
                1. 使用 GitHub Actions（scheduled workflow）或外部 cron 服務（cron-job.org、Render Cron 等）定時執行：
                   ```
                   0 8,18 * * * cd /path/to/ai-daily-app && python3 update_cache.py
                   ```
                2. 開啟本 App 時會自動判斷快取是否過期並刷新（無人瀏覽也會在有人開啟時更新）。
                3. 手動觸發：直接在本機或伺服器執行 `python update_cache.py`。

                這樣即可接近「每天 08:00 / 18:00 自動刷新」的體驗。
                """
            )

    # ========== 頁首 ==========
    st.markdown('<p class="main-header">每日 AI 資訊中心</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">彙整 AI 新聞、Threads 台港話題、香港與國際熱門頭條</p>',
        unsafe_allow_html=True,
    )

    # 頂部也放一個搜尋列（更醒目）
    top_search = st.text_input(
        "🔎 快速搜尋所有新聞標題與摘要",
        value=search_query or initial_search,
        key="top_search",
        placeholder="例如：OpenAI、NVIDIA、Agent...",
    ).strip()
    # 讓兩個搜尋框同步（以較新的為主）
    effective_query = top_search or search_query or initial_search
    if effective_query != st.session_state.get("global_search", ""):
        st.session_state["global_search"] = effective_query

    # 載入資料
    with st.spinner("正在載入最新資訊..."):
        data, refreshed = get_daily_data(force_refresh=force_refresh)

    analysis = get_analysis_payload(data)
    tracked_keys = get_tracked_giant_keys()

    # 指標列
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("快取時段", data.get("slot", "—"))
    col2.metric("板塊數量", len(data.get("sections", [])) + 1)
    col3.metric("文章總數", sum(s.get("count", 0) for s in data.get("sections", [])))
    col4.metric("下次更新", data.get("next_refresh", next_label))

    if refreshed:
        st.success(f"已更新至最新資料（{format_updated_at(data.get('updated_at'))}）")
    else:
        st.info(f"使用目前快取（上次更新：{format_updated_at(data.get('updated_at'))}）")

    # 搜尋結果提示
    if effective_query:
        st.markdown(
            f'<div class="search-result-banner">🔍 目前搜尋：「{html.escape(effective_query)}」'
            f'（符合的項目會優先顯示，點擊卡片仍可開啟原文）</div>',
            unsafe_allow_html=True,
        )

    # ========== 分頁 ==========
    tab_labels = [f"📊 {analysis['title']}"] + [
        f"{s['icon']} {s['title']}" for s in data.get("sections", [])
    ]
    tabs = st.tabs(tab_labels)

    # ---- 📊 每日重點分析 ----
    with tabs[0]:
        st.markdown(f"**{analysis['description']}**")
        if tracked_keys:
            st.caption("已啟用自訂追蹤巨頭優先排序：" + "、".join(tracked_labels))
        st.caption(
            f"共 {analysis.get('count', 0)} 條重點 · "
            f"分析生成時間（香港時間）：{analysis.get('generated_at', '未知')}"
        )

        # Highlights：先過濾再優先排序
        highlights = analysis.get("highlights", [])
        if effective_query:
            highlights = _filter_by_query(
                highlights, effective_query, ["event", "importance", "regional"]
            )
        highlights = _prioritize_tracked(highlights, tracked_keys, lambda x: f"{x.get('event','')} {x.get('importance','')}")

        if not highlights:
            if effective_query:
                st.warning("目前搜尋條件下沒有符合的重點分析項目。")
            else:
                st.warning("暫時無法產生重點分析，請稍後再試或點擊「立即更新」。")
        else:
            for index, highlight in enumerate(highlights, start=1):
                render_highlight(highlight, index, search_query=effective_query, tracked_keys=tracked_keys)

        # AI Agent 與巨頭動態
        agent_giants = analysis.get("agent_giants", {})
        st.markdown(
            f'<div class="subsection-title">'
            f'{agent_giants.get("icon", "🌐")} {agent_giants.get("title", "AI Agent 與巨頭動態")}'
            f'</div>',
            unsafe_allow_html=True,
        )
        if tracked_keys:
            st.caption("追蹤巨頭相關已自動置頂")
        st.markdown(f"**{agent_giants.get('description', '')}**")
        st.caption(
            f"共 {agent_giants.get('count', 0)} 則動態 · "
            f"分析生成時間（香港時間）：{agent_giants.get('generated_at', analysis.get('generated_at', '未知'))}"
        )

        giant_items = agent_giants.get("items", [])
        if effective_query:
            giant_items = _filter_by_query(giant_items, effective_query, ["event", "giant"])
        giant_items = _prioritize_tracked(giant_items, tracked_keys, lambda x: f"{x.get('event','')} {x.get('giant','')}")

        if not giant_items:
            if effective_query:
                st.warning("目前搜尋條件下沒有符合的巨頭動態。")
            else:
                st.warning("暫時無法產生 Agent 與巨頭動態，請稍後再試或點擊「立即更新」。")
        else:
            for index, item in enumerate(giant_items, start=1):
                render_agent_giant_item(item, index, search_query=effective_query, tracked_keys=tracked_keys)

    # ---- 其他板塊 ----
    for tab, section in zip(tabs[1:], data.get("sections", [])):
        with tab:
            st.markdown(f"**{section['description']}**")
            st.caption(f"共 {section.get('count', 0)} 則")

            articles = section.get("articles", [])
            if effective_query:
                articles = _filter_by_query(
                    articles, effective_query, ["title", "summary", "ai_summary"]
                )

            if not articles:
                if effective_query:
                    st.warning("目前搜尋條件下沒有符合的新聞。")
                else:
                    st.warning("暫時無法取得新聞，請稍後再試或點擊「立即更新」。")
                continue

            show_ai_summary = section.get("key") in {
                "ai_news",
                "threads_tw",
                "threads_hk",
            }
            for article in articles:
                render_article(article, show_ai_summary=show_ai_summary, search_query=effective_query)


if __name__ == "__main__":
    main()