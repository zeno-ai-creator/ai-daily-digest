#!/usr/bin/env python3
"""每日背景更新腳本，可搭配 cron / GitHub Actions / 手動觸發使用。

用法：
  python update_cache.py
  python update_cache.py --verbose

建議 cron（香港時間 08:00 / 18:00）：
  0 8,18 * * * cd /path/to/ai-daily-app && /usr/bin/env python3 update_cache.py >> /tmp/ai-daily-cache.log 2>&1
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from cache import get_current_hk_time_label, next_refresh_label, refresh_cache


HK_TZ = ZoneInfo("Asia/Hong_Kong")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Daily 快取更新工具")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="顯示更多更新細節"
    )
    args = parser.parse_args()

    print(f"[{get_current_hk_time_label()}] 開始執行快取更新...")

    try:
        payload = refresh_cache()
    except Exception as exc:  # noqa: BLE001
        print(f"❌ 更新失敗：{exc}", file=sys.stderr)
        sys.exit(1)

    updated = payload.get("updated_at", "未知")
    slot = payload.get("slot", "未知")
    next_refresh = payload.get("next_refresh") or next_refresh_label()

    print(f"✅ 快取更新成功")
    print(f"   日期/時段：{payload.get('date')} ({slot})")
    print(f"   更新時間：{updated}")
    print(f"   下次更新：{next_refresh}")

    sections = payload.get("sections", [])
    total = sum(s.get("count", 0) for s in sections)
    print(f"   總文章數：{total} 則（共 {len(sections)} 板塊）")

    if args.verbose:
        for section in sections:
            print(f"     • {section.get('title')}: {section.get('count', 0)} 則")
        analysis = payload.get("daily_analysis", {})
        print(f"   重點分析：{analysis.get('count', 0)} 條")
        giants = analysis.get("agent_giants", {})
        print(f"   巨頭動態：{giants.get('count', 0)} 則")

    print(f"下次背景刷新時間（香港時間）：{next_refresh}")


if __name__ == "__main__":
    main()