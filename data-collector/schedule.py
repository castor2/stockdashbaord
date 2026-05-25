#!/usr/bin/env python3
"""
매일 1회 데이터 수집 스케줄러.

- 컨테이너 시작 시 즉시 1회 수집
- 이후 COLLECT_DAILY_AT 시각(기본 09:00, TZ=Asia/Seoul)에 매일 수집
"""

import logging
import os
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from collect import main as run_collection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

TZ_NAME = os.environ.get("TZ", "Asia/Seoul")
DAILY_AT = os.environ.get("COLLECT_DAILY_AT", "09:00")


def parse_daily_at(value: str) -> tuple[int, int]:
    parts = value.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"COLLECT_DAILY_AT must be HH:MM, got: {value!r}")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid COLLECT_DAILY_AT: {value!r}")
    return hour, minute


def next_run_at(tz: ZoneInfo, hour: int, minute: int) -> datetime:
    now = datetime.now(tz)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target


def sleep_until(target: datetime) -> None:
    tz = target.tzinfo
    assert tz is not None
    seconds = max(0, int((target - datetime.now(tz)).total_seconds()))
    logger.info(
        "다음 수집 예정: %s (%s, %d초 후)",
        target.strftime("%Y-%m-%d %H:%M:%S %Z"),
        TZ_NAME,
        seconds,
    )
    time.sleep(seconds)


def main() -> None:
    try:
        tz = ZoneInfo(TZ_NAME)
        hour, minute = parse_daily_at(DAILY_AT)
    except Exception as exc:
        logger.error("스케줄 설정 오류: %s", exc)
        sys.exit(1)

    logger.info("매일 %02d:%02d (%s) 데이터 수집 스케줄러 시작", hour, minute, TZ_NAME)

    while True:
        logger.info("━━ 데이터 수집 시작 ━━")
        try:
            exit_code = run_collection()
            if exit_code != 0:
                logger.warning("수집 완료 (일부 오류, exit=%d)", exit_code)
            else:
                logger.info("수집 완료")
        except Exception:
            logger.exception("수집 중 예외 발생")

        sleep_until(next_run_at(tz, hour, minute))


if __name__ == "__main__":
    main()
