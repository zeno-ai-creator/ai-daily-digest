from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from urllib.parse import quote_plus

from .rss import fetch_rss
from .scoring import THREADS_KEYWORDS, rank_articles
from .summarize import enrich_with_summary

AI_QUERY = (
    "AI OR 人工智慧 OR LLM OR Agent OR ChatGPT OR OpenAI OR Gemini OR Claude"
)
THREADS_QUERY = f"Threads ({AI_QUERY}) OR Meta Threads 人工智慧"

SECTION_CONFIG: dict[str, dict[str, Any]] = {
    "ai_news": {
        "title": "AI 新聞",
        "icon": "🤖",
        "description": "優先顯示最新、高相關 AI 動態，附簡要重點摘要",
        "feeds": [
            (
                "https://news.google.com/rss/search?q="
                + quote_plus("人工智慧 OR AI OR ChatGPT OR OpenAI OR LLM OR Agent")
                + "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            ),
            (
                "https://news.google.com/rss/search?q="
                + quote_plus(
                    "artificial intelligence OR machine learning OR LLM OR AI agent"
                )
                + "&hl=en-US&gl=US&ceid=US:en"
            ),
        ],
        "limit": 18,
        "prioritize_ai": True,
        "add_ai_summary": True,
    },
    "threads_tw": {
        "title": "Threads 台灣",
        "icon": "🧵",
        "description": "台灣 Threads 與社群 AI 相關熱門話題",
        "feeds": [
            (
                "https://news.google.com/rss/search?q="
                + quote_plus(THREADS_QUERY)
                + "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            ),
            (
                "https://news.google.com/rss/search?q="
                + quote_plus("Threads AI OR Threads 人工智慧 OR Threads LLM")
                + "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            ),
        ],
        "limit": 12,
        "prioritize_ai": True,
        "extra_keywords": THREADS_KEYWORDS,
        "add_ai_summary": True,
    },
    "threads_hk": {
        "title": "Threads 香港",
        "icon": "🧶",
        "description": "香港 Threads 與社群 AI 相關熱門話題",
        "feeds": [
            (
                "https://news.google.com/rss/search?q="
                + quote_plus(THREADS_QUERY)
                + "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
            ),
            (
                "https://news.google.com/rss/search?q="
                + quote_plus("Threads AI OR Threads 人工智慧 OR Threads Agent")
                + "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
            ),
        ],
        "limit": 12,
        "prioritize_ai": True,
        "extra_keywords": THREADS_KEYWORDS,
        "add_ai_summary": True,
    },
    "hk_news": {
        "title": "香港 Google 新聞",
        "icon": "🇭🇰",
        "description": "香港本地與區域頭條新聞",
        "feeds": [
            "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant",
        ],
        "limit": 15,
        "prioritize_ai": False,
        "add_ai_summary": False,
    },
    "international": {
        "title": "國際熱門話題",
        "icon": "🌍",
        "description": "全球國際新聞與熱門頭條",
        "feeds": [
            "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
            (
                "https://news.google.com/rss/search?q="
                + quote_plus("world news OR international")
                + "&hl=en-US&gl=US&ceid=US:en"
            ),
        ],
        "limit": 15,
        "prioritize_ai": False,
        "add_ai_summary": False,
    },
}


def _dedupe_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for article in articles:
        key = article.get("link") or article.get("title", "")
        if key in seen:
            continue
        seen.add(key)
        unique.append(article)
    return unique


def fetch_section(section_key: str) -> dict[str, Any]:
    config = SECTION_CONFIG[section_key]
    articles: list[dict[str, Any]] = []
    fetch_errors: list[str] = []

    for feed_url in config["feeds"]:
        try:
            articles.extend(fetch_rss(feed_url, limit=config["limit"]))
        except Exception as exc:
            fetch_errors.append(f"{feed_url}: {exc}")

    articles = [a for a in _dedupe_articles(articles) if not a.get("error")]
    articles = rank_articles(
        articles,
        prioritize_ai=config.get("prioritize_ai", False),
        extra_keywords=config.get("extra_keywords"),
    )
    articles = articles[: config["limit"]]

    if config.get("add_ai_summary"):
        articles = enrich_with_summary(articles)

    return {
        "key": section_key,
        "title": config["title"],
        "icon": config["icon"],
        "description": config["description"],
        "articles": articles,
        "count": len(articles),
        "errors": fetch_errors,
    }


def fetch_all_sections() -> dict[str, Any]:
    sections: dict[str, Any] = {}

    with ThreadPoolExecutor(max_workers=len(SECTION_CONFIG)) as executor:
        futures = {
            executor.submit(fetch_section, key): key for key in SECTION_CONFIG
        }
        for future in as_completed(futures):
            section = future.result()
            sections[section["key"]] = section

    return {
        "sections": [sections[key] for key in SECTION_CONFIG],
        "section_map": sections,
    }