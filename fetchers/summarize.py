from __future__ import annotations

import re
from typing import Any

SOURCE_SUFFIX = re.compile(r"\s*[-–—]\s*[^-–—]+$")
NOISE = re.compile(r"&nbsp;|&amp;|&lt;|&gt;")
SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?])\s+")


def _clean_text(text: str) -> str:
    text = NOISE.sub(" ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _strip_source_from_title(title: str) -> str:
    return SOURCE_SUFFIX.sub("", title).strip()


def summarize_article(article: dict[str, Any]) -> str:
    title = _strip_source_from_title(article.get("title", ""))
    summary = _clean_text(article.get("summary", ""))

    if summary and summary != title:
        sentences = [s.strip() for s in SENTENCE_SPLIT.split(summary) if s.strip()]
        lead = sentences[0] if sentences else summary
        if len(lead) > 120:
            lead = lead[:117] + "..."
        return f"重點：{lead}"

    if len(title) > 90:
        return f"重點：{title[:87]}..."
    return f"重點：{title}"


def enrich_with_summary(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for article in articles:
        item = dict(article)
        item["ai_summary"] = summarize_article(item)
        enriched.append(item)
    return enriched