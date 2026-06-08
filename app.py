from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

from cache import get_daily_data, next_refresh_label
from fetchers.daily_analysis import generate_daily_analysis

st.set_page_config(
    page_title="每日 AI 資訊中心",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #9CA3AF;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .section-card {
        background: #1A1F2E;
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s ease;
    }
    .section-card:hover {
        border-color: #3B82F6;
    }
    .article-title {
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
        line-height: 1.45;
    }
    .article-meta {
        color: #9CA3AF;
        font-size: 0.85rem;
        margin-bottom: 0.45rem;
    }
    .article-summary {
        color: #CBD5E1;
        font-size: 0.92rem;
        line-height: 1.5;
        margin-top: 0.2rem;
    }
    .analysis-label {
        color: #93C5FD;
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 0.55rem;
        margin-bottom: 0.15rem;
    }
    .analysis-text {
        color: #CBD5E1;
        font-size: 0.92rem;
        line-height: 1.55;
        margin-bottom: 0.2rem;
    }
    .ai-badge {
        display: inline-block;
        background: #1E3A5F;
        color: #93C5FD;
        font-size: 0.75rem;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        margin-left: 0.4rem;
        vertical-align: middle;
    }
    .subsection-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin: 1.6rem 0 0.6rem 0;
        color: #E2E8F0;
    }
    .agent-card-blue {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
        border: 1px solid #3B82F6;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .agent-card-blue:hover {
        border-color: #60A5FA;
        box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.35);
    }
    .agent-card-green {
        background: linear-gradient(135deg, #0F172A 0%, #14532D 100%);
        border: 1px solid #22C55E;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .agent-card-green:hover {
        border-color: #4ADE80;
        box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.35);
    }
    .giant-badge-blue {
        display: inline-block;
        background: #1D4ED8;
        color: #DBEAFE;
        font-size: 0.75rem;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        margin-left: 0.4rem;
        vertical-align: middle;
    }
    .giant-badge-green {
        display: inline-block;
        background: #15803D;
        color: #DCFCE7;
        font-size: 0.75rem;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        margin-left: 0.4rem;
        vertical-align: middle;
    }
    .agent-label-blue { color: #93C5FD; }
    .agent-label-green { color: #86EFAC; }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_updated_at(value: str | None) -> str:
    if not value:
        return "未知"
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%Y年%m月%d日 %H:%M")
    except ValueError:
        return value


def get_analysis_payload(data: dict) -> dict:
    analysis = data.get("daily_analysis")
    if analysis and analysis.get("highlights") and analysis.get("agent_giants"):
        return analysis
    return generate_daily_analysis(data.get("sections", []))


def render_agent_giant_item(item: dict, index: int) -> None:
    event = html.escape(item.get("event", ""))
    importance = html.escape(item.get("importance", ""))
    regional = html.escape(item.get("regional", ""))
    giant = html.escape(item.get("giant", ""))
    source = html.escape(item.get("source", ""))
    link = html.escape(item.get("link", "#"), quote=True)
    card_style = item.get("card_style", "blue")

    card_class = "agent-card-blue" if card_style == "blue" else "agent-card-green"
    badge_class = "giant-badge-blue" if card_style == "blue" else "giant-badge-green"
    label_class = "agent-label-blue" if card_style == "blue" else "agent-label-green"
    meta = f"參考來源：{source}" if source else "參考來源：新聞彙整"

    st.markdown(
        f"""
        <div class="{card_class}">
            <div class="article-title">
                {index}. {event}
                <span class="{badge_class}">{giant}</span>
            </div>
            <div class="article-meta">
                <a href="{link}" target="_blank" style="color: #9CA3AF; text-decoration: none;">
                    {meta}
                </a>
            </div>
            <div class="analysis-label {label_class}">🌐 國際重點</div>
            <div class="analysis-text">{event}</div>
            <div class="analysis-label {label_class}">⚡ 重要性（全球影響）</div>
            <div class="analysis-text">{importance}</div>
            <div class="analysis-label {label_class}">🇭🇰🇹🇼 對香港／台灣影響</div>
            <div class="analysis-text">{regional}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_highlight(highlight: dict, index: int) -> None:
    event = html.escape(highlight.get("event", ""))
    importance = html.escape(highlight.get("importance", ""))
    regional = html.escape(highlight.get("regional", ""))
    source = html.escape(highlight.get("source", ""))
    link = html.escape(highlight.get("link", "#"), quote=True)

    meta = f"參考來源：{source}" if source else "參考來源：新聞彙整"

    st.markdown(
        f"""
        <div class="section-card">
            <div class="article-title">
                {index}. {event}
            </div>
            <div class="article-meta">
                <a href="{link}" target="_blank" style="color: #9CA3AF; text-decoration: none;">
                    {meta}
                </a>
            </div>
            <div class="analysis-label">🌐 國際核心事件／趨勢</div>
            <div class="analysis-text">{event}</div>
            <div class="analysis-label">⚡ 為什麼重要（全球影響）</div>
            <div class="analysis-text">{importance}</div>
            <div class="analysis-label">🇭🇰🇹🇼 對香港／台灣的可能影響或機會</div>
            <div class="analysis-text">{regional}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_article(article: dict, *, show_ai_summary: bool = False) -> None:
    title = html.escape(article.get("title", "無標題"))
    link = html.escape(article.get("link", "#"), quote=True)
    summary = html.escape(article.get("summary", ""))
    ai_summary = html.escape(article.get("ai_summary", ""))
    published = html.escape(article.get("published") or "")
    source = html.escape(article.get("source", ""))
    ai_score = article.get("ai_score")

    meta_parts = [part for part in [source, published] if part]
    meta = " · ".join(meta_parts) if meta_parts else "來源未知"

    badge = ""
    if ai_score and ai_score >= 8:
        badge = f'<span class="ai-badge">AI 相關度 {ai_score}</span>'

    summary_html = ""
    if show_ai_summary and ai_summary:
        summary_html = f'<div class="article-summary">{ai_summary}</div>'
    elif summary:
        clipped = summary[:180] + ("..." if len(summary) > 180 else "")
        summary_html = f'<div class="article-summary">{clipped}</div>'

    st.markdown(
        f"""
        <div class="section-card">
            <div class="article-title">
                <a href="{link}" target="_blank" style="color: #E2E8F0; text-decoration: none;">
                    {title}
                </a>
                {badge}
            </div>
            <div class="article-meta">{meta}</div>
            {summary_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    with st.sidebar:
        st.title("📰 每日資訊")
        st.markdown("---")
        st.markdown("**六大板塊**")
        st.markdown("- 📊 每日重點分析")
        st.markdown("- 🤖 AI 新聞（高相關排序 + 摘要）")
        st.markdown("- 🧵 Threads 台灣")
        st.markdown("- 🧶 Threads 香港")
        st.markdown("- 🇭🇰 香港 Google 新聞")
        st.markdown("- 🌍 國際熱門話題")
        st.markdown("---")
        st.caption("快取每 12 小時更新一次，排程為香港時間 08:00 與 18:00。")

        force_refresh = st.button("🔄 立即更新", use_container_width=True)

    st.markdown('<p class="main-header">每日 AI 資訊中心</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">彙整 AI 新聞、Threads 台港話題、香港與國際熱門頭條</p>',
        unsafe_allow_html=True,
    )

    with st.spinner("正在載入最新資訊..."):
        data, refreshed = get_daily_data(force_refresh=force_refresh)

    analysis = get_analysis_payload(data)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("快取時段", data.get("slot", "—"))
    col2.metric("板塊數量", len(data.get("sections", [])) + 1)
    col3.metric("文章總數", sum(s.get("count", 0) for s in data.get("sections", [])))
    col4.metric("下次更新", data.get("next_refresh", next_refresh_label()))

    if refreshed:
        st.success(f"已更新至最新資料（{format_updated_at(data.get('updated_at'))}）")
    else:
        st.info(f"使用目前快取（上次更新：{format_updated_at(data.get('updated_at'))}）")

    tab_labels = [f"📊 {analysis['title']}"] + [
        f"{s['icon']} {s['title']}" for s in data.get("sections", [])
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        st.markdown(f"**{analysis['description']}**")
        st.caption(
            f"共 {analysis.get('count', 0)} 條重點 · "
            f"分析生成時間（香港時間）：{analysis.get('generated_at', '未知')}"
        )

        highlights = analysis.get("highlights", [])
        if not highlights:
            st.warning("暫時無法產生重點分析，請稍後再試或點擊「立即更新」。")
        else:
            for index, highlight in enumerate(highlights, start=1):
                render_highlight(highlight, index)

        agent_giants = analysis.get("agent_giants", {})
        st.markdown(
            f'<div class="subsection-title">'
            f'{agent_giants.get("icon", "🌐")} {agent_giants.get("title", "AI Agent 與巨頭動態")}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"**{agent_giants.get('description', '')}**")
        st.caption(
            f"共 {agent_giants.get('count', 0)} 則動態 · "
            f"分析生成時間（香港時間）：{agent_giants.get('generated_at', analysis.get('generated_at', '未知'))}"
        )

        giant_items = agent_giants.get("items", [])
        if not giant_items:
            st.warning("暫時無法產生 Agent 與巨頭動態，請稍後再試或點擊「立即更新」。")
        else:
            for index, item in enumerate(giant_items, start=1):
                render_agent_giant_item(item, index)

    for tab, section in zip(tabs[1:], data.get("sections", [])):
        with tab:
            st.markdown(f"**{section['description']}**")
            st.caption(f"共 {section.get('count', 0)} 則")

            articles = section.get("articles", [])
            if not articles:
                st.warning("暫時無法取得新聞，請稍後再試或點擊「立即更新」。")
                continue

            show_ai_summary = section.get("key") in {
                "ai_news",
                "threads_tw",
                "threads_hk",
            }
            for article in articles:
                render_article(article, show_ai_summary=show_ai_summary)


if __name__ == "__main__":
    main()