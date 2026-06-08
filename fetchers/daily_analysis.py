from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from .summarize import _clean_text, _strip_source_from_title

HK_TZ = ZoneInfo("Asia/Hong_Kong")

SOURCE_SECTIONS = ("ai_news", "threads_tw", "threads_hk")
ANALYSIS_MIN = 4
ANALYSIS_MAX = 6

INTERNATIONAL_KEYWORDS: dict[str, int] = {
    "openai": 10,
    "chatgpt": 9,
    "google": 9,
    "gemini": 9,
    "anthropic": 10,
    "claude": 9,
    "meta": 8,
    "xai": 10,
    "grok": 8,
    "microsoft": 8,
    "nvidia": 8,
    "deepmind": 9,
    "llm": 7,
    "agent": 7,
    "代理式": 7,
    "生成式": 7,
    "artificial intelligence": 6,
    "machine learning": 6,
    "全球": 6,
    "國際": 6,
    "international": 6,
    "global": 6,
    "world": 5,
    "frontier": 6,
    "model": 4,
    "大語言模型": 7,
}

LOCAL_PENALTY_KEYWORDS: dict[str, int] = {
    "台股": -8,
    "港股": -8,
    "跌停": -6,
    "漲停": -6,
    "股價": -5,
    "收盤": -5,
    "大盤": -5,
}

THEME_RULES: list[dict[str, Any]] = [
    {
        "theme": "openai",
        "patterns": [r"openai", r"chatgpt", r"sora"],
        "importance": (
            "OpenAI 的產品路線與商業化節奏，直接影響全球生成式 AI 競爭格局、"
            "API 定價與超級應用（Super App）發展方向。"
        ),
        "regional": (
            "港台新創與企業可提前評估 OpenAI 生態整合，並關注模型授權、"
            "資料跨境與企業級部署成本變化。"
        ),
    },
    {
        "theme": "google",
        "patterns": [r"google", r"gemini", r"deepmind", r"alphabet"],
        "importance": (
            "Google 在多模態模型與搜尋/雲端整合上的進展，將重塑資訊取得方式"
            "與企業 AI 工作流入口。"
        ),
        "regional": (
            "港台內容與廣告產業需調整 SEO 與內容策略；開發者可善用 Gemini API "
            "與 Google Cloud 方案加速產品落地。"
        ),
    },
    {
        "theme": "anthropic",
        "patterns": [r"anthropic", r"claude"],
        "importance": (
            "Anthropic 在安全對齊與企業級 Agent 上的布局，代表高可靠 AI 助理"
            "成為大型組織採用的關鍵指標。"
        ),
        "regional": (
            "港台金融、法律與醫療等高合規產業，可評估 Claude 在長文本與"
            "風險控制場景的導入機會。"
        ),
    },
    {
        "theme": "meta",
        "patterns": [r"\bmeta\b", r"threads", r"llama"],
        "importance": (
            "Meta 結合社群平台與開源/閉源模型的策略，影響 AI 內容分發、"
            "社群互動與廣告變現的下一階段。"
        ),
        "regional": (
            "港台品牌與創作者可關注 Threads 上的 AI 話題流量，並布局社群"
            "行銷與本地化內容生成工具。"
        ),
    },
    {
        "theme": "xai",
        "patterns": [r"\bxai\b", r"\bgrok\b", r"elon musk"],
        "importance": (
            "xAI 與 Grok 等挑戰者加速迭代，推升全球模型性能競賽強度，"
            "也影響開源與閉源陣營的技術節奏。"
        ),
        "regional": (
            "港台科技投資人與開發社群可追蹤新模型能力邊界，尋找替代方案"
            "與多模型備援策略。"
        ),
    },
    {
        "theme": "agent",
        "patterns": [r"\bagent\b", r"代理式", r"自主", r"autonomous"],
        "importance": (
            "代理式 AI（AI Agent）從對話走向任務執行，正在改寫企業自動化、"
            "軟體開發與客戶服務的全球投資優先順序。"
        ),
        "regional": (
            "港台企業可從客服、營運與內部知識管理試點 Agent，"
            "並建立人機協作與資安審查流程。"
        ),
    },
    {
        "theme": "infra",
        "patterns": [r"nvidia", r"晶片", r"chip", r"gpu", r"data center", r"資料中心"],
        "importance": (
            "算力、晶片與資料中心建設仍是全球 AI 擴張的底層瓶頸，"
            "直接決定模型訓練成本與推理服務供給。"
        ),
        "regional": (
            "港台雲端與硬體供應鏈可關注區域機房與邊緣推理需求，"
            "把握企業本地化部署與成本優化服務機會。"
        ),
    },
    {
        "theme": "policy",
        "patterns": [r"法規", r"監管", r"regulation", r"policy", r"ban", r"安全"],
        "importance": (
            "各國 AI 監管與安全標準持續演進，將影響模型上線時程、"
            "跨境資料流與大型科技公司的合規成本。"
        ),
        "regional": (
            "港台政府與企業需同步關注個資、生成內容責任與產業指引，"
            "降低產品出海與跨區營運的法規不確定性。"
        ),
    },
]

DEFAULT_IMPORTANCE = (
    "此動向反映全球 AI 產業在技術、資本與應用場景上的持續加速，"
    "將影響下一季產品競爭與投資配置。"
)
DEFAULT_REGIONAL = (
    "港台市場可從人才培訓、企業導入與新創孵化三方面著手，"
    "把國際趨勢轉化為本地化產品與服務機會。"
)

AGENT_KEYWORDS: dict[str, int] = {
    "agent": 8,
    "agents": 8,
    "代理式": 8,
    "代理": 5,
    "autonomous": 7,
    "multi-agent": 8,
    "自主": 5,
    "編排": 4,
    "orchestrat": 5,
    "copilot": 5,
    "assistant": 4,
}

PRODUCT_INVEST_KEYWORDS: dict[str, int] = {
    "投資": 6,
    "investment": 6,
    "funding": 6,
    "募資": 6,
    "融資": 6,
    "billion": 5,
    "launch": 5,
    "發布": 5,
    "推出": 5,
    "update": 4,
    "升級": 5,
    "product": 4,
    "產品": 4,
    "super app": 5,
    "超級應用": 5,
}

AGENT_GIANT_MIN = 4
AGENT_GIANT_MAX = 6

GIANT_RULES: list[dict[str, Any]] = [
    {
        "giant": "openai",
        "label": "OpenAI",
        "patterns": [r"openai", r"chatgpt", r"sam altman"],
        "card_style": "blue",
        "agent_importance": (
            "OpenAI 在 Agent 編排、工具調用與超級應用上的推進，"
            "正重新定義全球 AI 產品的預設互動方式與商業化節奏。"
        ),
        "agent_regional": (
            "港台 SaaS 與企業服務商可評估接入 OpenAI Agent 工具鏈，"
            "並針對在地語言、法規與產業流程做場景化封裝。"
        ),
        "product_importance": (
            "OpenAI 產品與融資節奏牽動全球模型供應鏈與 API 定價，"
            "是觀察生成式 AI 產業景氣的核心指標。"
        ),
        "product_regional": (
            "港台新創應提早規劃模型成本與供應韌性，"
            "並把握企業導入與顧問服務需求上升的機會。"
        ),
    },
    {
        "giant": "xai",
        "label": "Elon Musk / xAI",
        "patterns": [r"\bxai\b", r"\bgrok\b", r"elon musk", r"馬斯克"],
        "card_style": "green",
        "agent_importance": (
            "xAI 與 Grok 強調即時資訊與開放語境，"
            "推升全球 Agent 在社群輿情與即時決策場景的競爭強度。"
        ),
        "agent_regional": (
            "港台媒體與社群平台可關注 Grok 類即時 Agent 對內容分發的影響，"
            "並評估多模型備援與事實查核機制。"
        ),
        "product_importance": (
            "Musk 體系的 AI 投資與產品節奏，往往快速改寫市場敘事"
            "並帶動資本與開發者社群跟進。"
        ),
        "product_regional": (
            "港台投資人與開發者宜追蹤 xAI 動向，"
            "在替代模型策略與跨境合作上保留彈性。"
        ),
    },
    {
        "giant": "nvidia",
        "label": "Jensen Huang / NVIDIA",
        "patterns": [r"nvidia", r"jen(sen)?\s*huang", r"黃仁勳", r"\bgpu\b", r"cuda"],
        "card_style": "green",
        "agent_importance": (
            "NVIDIA 將 Agent 工作負載與推理晶片、軟體棧深度綁定，"
            "直接影響全球 Agent 部署成本與效能上限。"
        ),
        "agent_regional": (
            "港台雲端與系統整合商可布局 Agent 推理優化服務，"
            "協助企業在成本、延遲與資安之間取得平衡。"
        ),
        "product_importance": (
            "NVIDIA 晶片與平台更新決定 AI 基礎建設投資方向，"
            "是 Agent 與大模型規模化的底層關鍵。"
        ),
        "product_regional": (
            "港台硬體供應鏈與資料中心業者可關注區域推理需求，"
            "提供在地化算力與企業導入方案。"
        ),
    },
    {
        "giant": "google",
        "label": "Google",
        "patterns": [r"google", r"gemini", r"deepmind", r"alphabet", r"sundar"],
        "card_style": "blue",
        "agent_importance": (
            "Google 把 Gemini Agent 嵌入搜尋、辦公與雲端工作流，"
            "推動 Agent 從實驗功能走向主流生產力入口。"
        ),
        "agent_regional": (
            "港台企業可評估 Google Workspace 與 GCP 的 Agent 能力，"
            "在文件、客服與內部知識管理先做 PoC。"
        ),
        "product_importance": (
            "Google 在多模態與搜尋整合上的進展，"
            "將改寫全球資訊入口與廣告技術供應鏈。"
        ),
        "product_regional": (
            "港台內容與行銷產業需調整 SEO 與內容策略，"
            "並善用 Google Cloud 生態加速產品落地。"
        ),
    },
    {
        "giant": "microsoft",
        "label": "Microsoft",
        "patterns": [r"microsoft", r"微軟", r"\bcopilot\b", r"azure"],
        "card_style": "blue",
        "agent_importance": (
            "Microsoft 以 Copilot 與 Azure Agent 服務推進企業級自動化，"
            "帶動全球 B2B Agent 採用與資安治理標準。"
        ),
        "agent_regional": (
            "港台企業可從 Office、Dynamics 與 Azure 既有環境導入 Agent，"
            "降低流程改造門檻並強化合規管理。"
        ),
        "product_importance": (
            "微軟在企業 AI 平台與代理式風險治理上的布局，"
            "影響大型組織導入 AI 的節奏與採購決策。"
        ),
        "product_regional": (
            "港台 B2B 服務商可發展 Copilot 客製整合與 SBOM 盤點顧問服務，"
            "協助企業安全上線 Agent。"
        ),
    },
    {
        "giant": "anthropic",
        "label": "Anthropic",
        "patterns": [r"anthropic", r"claude"],
        "card_style": "green",
        "agent_importance": (
            "Anthropic 強調可控、可審計的 Agent 執行，"
            "成為高風險產業導入自主代理的重要參考。"
        ),
        "agent_regional": (
            "港台金融、醫療與法律機構可優先評估 Claude Agent，"
            "在長文本與風險控制場景建立示範案例。"
        ),
        "product_importance": (
            "Anthropic 的安全對齊路線影響全球企業級 AI 採購標準，"
            "也牽動模型能力與合規要求的平衡。"
        ),
        "product_regional": (
            "港台高合規產業可藉 Claude 生態建立可信 AI 服務，"
            "形成跨境輸出優勢。"
        ),
    },
    {
        "giant": "meta",
        "label": "Meta",
        "patterns": [r"\bmeta\b", r"threads", r"llama", r"zuckerberg"],
        "card_style": "blue",
        "agent_importance": (
            "Meta 把 Agent 能力導入 Threads、IG 與 Messenger 商業場景，"
            "加速社群電商與客服自動化的全球滲透。"
        ),
        "agent_regional": (
            "港台品牌與電商可測試 Meta 社群 Agent 工具，"
            "結合在地內容與轉換漏斗優化。"
        ),
        "product_importance": (
            "Meta 的開源模型與社群平台整合，"
            "影響內容分發、廣告變現與開發者工具供給。"
        ),
        "product_regional": (
            "港台創作者與行銷團隊可布局 Threads AI 話題經營，"
            "搶佔社群流量紅利。"
        ),
    },
]


def _now_hk_label() -> str:
    return datetime.now(HK_TZ).strftime("%Y年%m月%d日 %H:%M")


def _article_text(article: dict[str, Any]) -> str:
    title = _strip_source_from_title(article.get("title", ""))
    summary = _clean_text(article.get("summary", ""))
    return _normalize(f"{title} {summary}")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def score_international(article: dict[str, Any]) -> int:
    haystack = _article_text(article).lower()
    score = article.get("ai_score", 0)

    for keyword, weight in INTERNATIONAL_KEYWORDS.items():
        if keyword.lower() in haystack:
            score += weight

    for keyword, penalty in LOCAL_PENALTY_KEYWORDS.items():
        if keyword.lower() in haystack:
            score += penalty

    source_section = article.get("source_section", "")
    if source_section == "ai_news":
        score += 3
    elif source_section in {"threads_tw", "threads_hk"}:
        score += 1

    return score


def detect_theme(text: str) -> dict[str, Any] | None:
    lowered = text.lower()
    for rule in THEME_RULES:
        if any(re.search(pattern, lowered) for pattern in rule["patterns"]):
            return rule
    return None


def detect_giant(text: str) -> dict[str, Any] | None:
    lowered = text.lower()
    for rule in GIANT_RULES:
        if any(re.search(pattern, lowered) for pattern in rule["patterns"]):
            return rule
    return None


def _keyword_score(text: str, keywords: dict[str, int]) -> int:
    lowered = text.lower()
    return sum(weight for keyword, weight in keywords.items() if keyword.lower() in lowered)


def _is_agent_related(text: str) -> bool:
    return _keyword_score(text, AGENT_KEYWORDS) >= 5


def _is_product_or_invest(text: str) -> bool:
    return _keyword_score(text, PRODUCT_INVEST_KEYWORDS) >= 4


def score_agent_giant(article: dict[str, Any]) -> int:
    text = _article_text(article)
    lowered = text.lower()
    giant = detect_giant(text)
    if not giant:
        return 0

    score = 10
    score += _keyword_score(text, AGENT_KEYWORDS)
    score += _keyword_score(text, PRODUCT_INVEST_KEYWORDS)
    score += article.get("ai_score", 0) // 2

    for keyword, penalty in LOCAL_PENALTY_KEYWORDS.items():
        if keyword.lower() in lowered:
            score += penalty

    if _is_agent_related(text):
        score += 8
    if _is_product_or_invest(text):
        score += 5

    return score


def _build_agent_giant_insight(article: dict[str, Any], giant: dict[str, Any]) -> dict[str, str]:
    text = _article_text(article)
    agent_focus = _is_agent_related(text)

    if agent_focus:
        importance = giant["agent_importance"]
        regional = giant["agent_regional"]
    else:
        importance = giant["product_importance"]
        regional = giant["product_regional"]

    return {
        "event": _event_from_article(article),
        "importance": importance,
        "regional": regional,
        "giant": giant["label"],
        "card_style": giant["card_style"],
        "source": article.get("source", ""),
        "link": article.get("link", ""),
    }


def _rank_agent_giant_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for article in candidates:
        text = _article_text(article)
        giant = detect_giant(text)
        if not giant:
            continue
        item = dict(article)
        item["giant_rule"] = giant
        item["agent_giant_score"] = score_agent_giant(item)
        item["agent_focus"] = _is_agent_related(text)
        item["product_focus"] = _is_product_or_invest(text)
        ranked.append(item)

    ranked.sort(
        key=lambda item: (item.get("agent_giant_score", 0), item.get("published_ts", 0)),
        reverse=True,
    )
    return ranked


def _append_agent_giant_items(
    ranked: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    used_giants: set[str],
    used_events: set[str],
    *,
    limit: int,
    unique_giants: bool,
    min_score: int,
    require_signal: bool,
) -> None:
    for article in ranked:
        if len(selected) >= limit:
            break

        giant_key = article["giant_rule"]["giant"]
        event_key = _event_from_article(article).lower()

        if unique_giants and giant_key in used_giants:
            continue
        if event_key in used_events:
            continue
        if article in selected:
            continue
        if article.get("agent_giant_score", 0) < min_score:
            continue
        if require_signal and not (
            article.get("agent_focus") or article.get("product_focus")
        ):
            continue

        selected.append(article)
        used_giants.add(giant_key)
        used_events.add(event_key)


def generate_agent_giants_dynamics(sections: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = _collect_candidate_articles(sections)
    ranked = _rank_agent_giant_candidates(candidates)

    selected: list[dict[str, Any]] = []
    used_giants: set[str] = set()
    used_events: set[str] = set()

    _append_agent_giant_items(
        ranked,
        selected,
        used_giants,
        used_events,
        limit=AGENT_GIANT_MAX,
        unique_giants=True,
        min_score=12,
        require_signal=True,
    )

    if len(selected) < AGENT_GIANT_MIN:
        _append_agent_giant_items(
            ranked,
            selected,
            used_giants,
            used_events,
            limit=AGENT_GIANT_MIN,
            unique_giants=False,
            min_score=10,
            require_signal=True,
        )

    if len(selected) < AGENT_GIANT_MIN:
        _append_agent_giant_items(
            ranked,
            selected,
            used_giants,
            used_events,
            limit=AGENT_GIANT_MIN,
            unique_giants=False,
            min_score=8,
            require_signal=False,
        )

    selected = selected[:AGENT_GIANT_MAX]
    items = [
        _build_agent_giant_insight(article, article["giant_rule"])
        for article in selected
    ]

    return {
        "title": "AI Agent 與巨頭動態",
        "icon": "🌐",
        "description": (
            "聚焦 Elon Musk/xAI、Jensen Huang/NVIDIA、Google、OpenAI 等國際巨頭，"
            "提煉 Agent 趨勢、投資與產品更新"
        ),
        "generated_at": _now_hk_label(),
        "generated_at_iso": datetime.now(HK_TZ).isoformat(timespec="seconds"),
        "items": items,
        "count": len(items),
    }


def _event_from_article(article: dict[str, Any]) -> str:
    event = _strip_source_from_title(article.get("title", ""))
    event = re.sub(r"\s*\|.*$", "", event).strip()
    if len(event) > 110:
        event = event[:107] + "..."
    return event


def _build_insight(article: dict[str, Any]) -> dict[str, str]:
    text = _article_text(article)
    theme = detect_theme(text)

    return {
        "event": _event_from_article(article),
        "importance": theme["importance"] if theme else DEFAULT_IMPORTANCE,
        "regional": theme["regional"] if theme else DEFAULT_REGIONAL,
        "source": article.get("source", ""),
        "link": article.get("link", ""),
    }


def _collect_candidate_articles(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    section_map = {section["key"]: section for section in sections}
    candidates: list[dict[str, Any]] = []

    for key in SOURCE_SECTIONS:
        section = section_map.get(key)
        if not section:
            continue
        for article in section.get("articles", []):
            item = dict(article)
            item["source_section"] = key
            item["international_score"] = score_international(item)
            candidates.append(item)

    candidates.sort(
        key=lambda item: (item.get("international_score", 0), item.get("published_ts", 0)),
        reverse=True,
    )
    return candidates


def generate_daily_analysis(sections: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = _collect_candidate_articles(sections)
    selected: list[dict[str, Any]] = []
    used_themes: set[str] = set()
    used_events: set[str] = set()

    for article in candidates:
        if len(selected) >= ANALYSIS_MAX:
            break

        text = _article_text(article)
        theme = detect_theme(text)
        theme_key = theme["theme"] if theme else None
        event_key = _event_from_article(article).lower()

        if theme_key and theme_key in used_themes:
            continue
        if event_key in used_events:
            continue
        if article.get("international_score", 0) < 6:
            continue

        selected.append(article)
        if theme_key:
            used_themes.add(theme_key)
        used_events.add(event_key)

    if len(selected) < ANALYSIS_MIN:
        for article in candidates:
            if len(selected) >= ANALYSIS_MIN:
                break
            event_key = _event_from_article(article).lower()
            if event_key in used_events:
                continue
            selected.append(article)
            used_events.add(event_key)

    highlights = [_build_insight(article) for article in selected[:ANALYSIS_MAX]]

    return {
        "title": "每日重點分析",
        "icon": "📊",
        "description": "以國際 AI 趨勢為主，提煉今日 Top 重點與港台機會",
        "generated_at": _now_hk_label(),
        "generated_at_iso": datetime.now(HK_TZ).isoformat(timespec="seconds"),
        "highlights": highlights,
        "count": len(highlights),
        "agent_giants": generate_agent_giants_dynamics(sections),
    }