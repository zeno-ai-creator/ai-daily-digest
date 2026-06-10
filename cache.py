from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from fetchers import fetch_all_sections
from fetchers.daily_analysis import generate_daily_analysis

CACHE_DIR = Path(__file__).parent / "data" / "cache"
CACHE_FILE = CACHE_DIR / "daily_news.json"
HK_TZ = ZoneInfo("Asia/Hong_Kong")
CACHE_TTL_HOURS = 12
REFRESH_HOURS = (8, 18)


def _now_hk() -> datetime:
    return datetime.now(HK_TZ)


def _now_iso() -> str:
    return _now_hk().isoformat(timespec="seconds")


def current_cache_slot(now: datetime | None = None) -> str:
    """依香港時間劃分快取時段：08:00 為上午、18:00 為下午。"""
    now = now or _now_hk()
    date_str = now.date().isoformat()

    if now.hour >= REFRESH_HOURS[1]:
        return f"{date_str}-pm"
    if now.hour >= REFRESH_HOURS[0]:
        return f"{date_str}-am"

    previous_day = (now - timedelta(days=1)).date().isoformat()
    return f"{previous_day}-pm"


def next_refresh_label(now: datetime | None = None) -> str:
    now = now or _now_hk()
    today = now.date()

    morning = datetime.combine(today, datetime.min.time(), tzinfo=HK_TZ).replace(
        hour=REFRESH_HOURS[0]
    )
    evening = datetime.combine(today, datetime.min.time(), tzinfo=HK_TZ).replace(
        hour=REFRESH_HOURS[1]
    )

    if now < morning:
        target = morning
    elif now < evening:
        target = evening
    else:
        target = morning + timedelta(days=1)

    return target.strftime("%Y年%m月%d日 %H:%M")


def get_current_hk_time_label() -> str:
    """回傳目前香港時間字串（供 UI 顯示）。"""
    return _now_hk().strftime("%Y年%m月%d日 %H:%M")


def get_next_refresh_datetime(now: datetime | None = None) -> datetime:
    """回傳下次預定刷新時間（datetime 物件，Asia/Hong_Kong）。"""
    now = now or _now_hk()
    today = now.date()
    morning = datetime.combine(today, datetime.min.time(), tzinfo=HK_TZ).replace(hour=REFRESH_HOURS[0])
    evening = datetime.combine(today, datetime.min.time(), tzinfo=HK_TZ).replace(hour=REFRESH_HOURS[1])

    if now < morning:
        return morning
    elif now < evening:
        return evening
    return morning + timedelta(days=1)


def format_updated_at(value: str | None) -> str:
    """格式化 updated_at 為繁體中文易讀字串。"""
    if not value:
        return "未知"
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=HK_TZ)
        else:
            dt = dt.astimezone(HK_TZ)
        return dt.strftime("%Y年%m月%d日 %H:%M")
    except (ValueError, TypeError):
        return value or "未知"


def load_cache() -> dict[str, Any] | None:
    if not CACHE_FILE.exists():
        return None
    try:
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_cache(payload: dict[str, Any]) -> dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


def _parse_updated_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=HK_TZ)
    return dt.astimezone(HK_TZ)


def is_cache_fresh(cache: dict[str, Any] | None) -> bool:
    if not cache:
        return False

    updated_at = _parse_updated_at(cache.get("updated_at"))
    if updated_at is None:
        return False

    now = _now_hk()
    age_hours = (now - updated_at).total_seconds() / 3600
    if age_hours >= CACHE_TTL_HOURS:
        return False

    return cache.get("slot") == current_cache_slot(now)


def refresh_cache() -> dict[str, Any]:
    now = _now_hk()
    data = fetch_all_sections()
    payload = {
        "date": now.date().isoformat(),
        "slot": current_cache_slot(now),
        "updated_at": _now_iso(),
        "cache_ttl_hours": CACHE_TTL_HOURS,
        "refresh_schedule": list(REFRESH_HOURS),
        "next_refresh": next_refresh_label(now),
        "sections": data["sections"],
        "daily_analysis": generate_daily_analysis(data["sections"]),
    }
    return save_cache(payload)


def get_daily_data(force_refresh: bool = False) -> tuple[dict[str, Any], bool]:
    if force_refresh:
        # 強化「立即更新」按鈕的強制清除快取功能：刪除快取檔、忽略 TTL/slot 直接重抓
        if CACHE_FILE.exists():
            try:
                CACHE_FILE.unlink()
            except Exception:
                pass
        return refresh_cache(), True

    cache = load_cache()
    if is_cache_fresh(cache):
        return cache, False

    return refresh_cache(), True