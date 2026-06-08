from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from xml.etree import ElementTree

import requests

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 20


def _clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError, OverflowError):
        return value


def _find_text(element: ElementTree.Element | None, tag: str) -> str:
    if element is None:
        return ""
    child = element.find(tag)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def fetch_rss(url: str, limit: int = 12) -> list[dict[str, Any]]:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    root = ElementTree.fromstring(response.content)
    channel = root.find("channel")
    items = root.findall(".//item") if channel is None else channel.findall("item")

    articles: list[dict[str, Any]] = []
    for item in items[:limit]:
        title = _find_text(item, "title")
        link = _find_text(item, "link")
        if not title or not link:
            continue

        source = _find_text(item, "source")
        if not source:
            source_match = re.search(r" - ([^-]+)$", title)
            source = source_match.group(1).strip() if source_match else ""

        articles.append(
            {
                "title": title,
                "link": link,
                "summary": _clean_html(_find_text(item, "description")),
                "published": _parse_date(_find_text(item, "pubDate")),
                "source": source,
            }
        )

    return articles