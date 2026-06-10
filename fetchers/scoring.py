from __future__ import annotations

import re
from datetime import datetime
from typing import Any

AI_KEYWORDS: dict[str, int] = {
    "人工智慧": 5,
    "生成式": 5,
    "ChatGPT": 5,
    "OpenAI": 5,
    "Gemini": 5,
    "Claude": 5,
    "LLM": 5,
    "Agent": 5,
    "代理式": 5,
    "大語言模型": 5,
    "機器學習": 4,
    "深度學習": 4,
    "AI": 4,
    "Meta AI": 4,
    "Anthropic": 4,
    "NVIDIA": 3,
    "微軟": 3,
    "Google": 3,
    "Threads": 3,
    "自動化": 2,
    "科技": 1,
    # Apple 相關來源權重（提高 AI 新聞與重點分析優先度）
    "WWDC": 8,
    "WWDC2026": 8,
    "Apple Intelligence": 8,
    "Siri AI": 7,
    "Siri": 6,
    "Apple": 5,
    "蘋果": 5,
    "蘋果智慧": 6,
}

THREADS_KEYWORDS: dict[str, int] = {
    "Threads": 6,
    "Meta": 4,
    "社群": 3,
    "話題": 3,
    "熱門": 2,
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def score_ai_relevance(article: dict[str, Any], extra_keywords: dict[str, int] | None = None) -> int:
    keywords = dict(AI_KEYWORDS)
    if extra_keywords:
        keywords.update(extra_keywords)

    haystack = _normalize(
        f"{article.get('title', '')} {article.get('summary', '')}"
    ).lower()

    score = 0
    for keyword, weight in keywords.items():
        if keyword.lower() in haystack:
            score += weight

    return score


def _parse_published_ts(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M").timestamp()
    except ValueError:
        return 0.0


def rank_articles(
    articles: list[dict[str, Any]],
    *,
    prioritize_ai: bool = False,
    extra_keywords: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for article in articles:
        item = dict(article)
        item["published_ts"] = _parse_published_ts(item.get("published"))
        if prioritize_ai:
            item["ai_score"] = score_ai_relevance(item, extra_keywords)
        enriched.append(item)

    if prioritize_ai:
        enriched.sort(
            key=lambda item: (item.get("ai_score", 0), item.get("published_ts", 0)),
            reverse=True,
        )
    else:
        enriched.sort(key=lambda item: item.get("published_ts", 0), reverse=True)

    return enriched