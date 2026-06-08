#!/usr/bin/env python3
"""每日背景更新腳本，可搭配 cron 使用。"""

from __future__ import annotations

from cache import refresh_cache


def main() -> None:
    payload = refresh_cache()
    print(f"快取已更新：{payload['date']} @ {payload['updated_at']}")
    for section in payload["sections"]:
        print(f"  - {section['title']}: {section['count']} 則")


if __name__ == "__main__":
    main()