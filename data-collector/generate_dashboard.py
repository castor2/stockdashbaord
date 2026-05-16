#!/usr/bin/env python3
"""
Grafana 대시보드 JSON 생성기
각 지표 = 상단 stat 패널(현재값 큰 숫자) + 하단 timeseries 패널(원래 그래프)
"""
import json

DS = {"type": "influxdb", "uid": "macro-influxdb"}

STAT_H = 3   # 숫자 패널 높이
TS_H   = 9   # 그래프 패널 높이 (원래와 동일)


# ── Flux 쿼리 ─────────────────────────────────────────────────
def flux_ts(measurement: str) -> str:
    """timeseries용: 선택 기간 + 기간 이전 마지막값 union (단기 조회 대응)"""
    return (
        f'union(\n'
        f'  tables: [\n'
        f'    from(bucket: "macro_indicators")\n'
        f'      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n'
        f'      |> filter(fn: (r) => r["_measurement"] == "{measurement}")\n'
        f'      |> filter(fn: (r) => r["_field"] == "value"),\n'
        f'    from(bucket: "macro_indicators")\n'
        f'      |> range(start: -5y, stop: v.timeRangeStart)\n'
        f'      |> filter(fn: (r) => r["_measurement"] == "{measurement}")\n'
        f'      |> filter(fn: (r) => r["_field"] == "value")\n'
        f'      |> last()\n'
        f'  ]\n'
        f')\n'
        f'|> sort(columns: ["_time"])'
    )

def flux_stat(measurement: str) -> str:
    """stat용: 항상 최근 5년 데이터 → lastNotNull이 반드시 값을 찾음"""
    return (
        f'from(bucket: "macro_indicators")\n'
        f'  |> range(start: -5y)\n'
        f'  |> filter(fn: (r) => r["_measurement"] == "{measurement}")\n'
        f'  |> filter(fn: (r) => r["_field"] == "value")\n'
        f'  |> last()'
    )


# ── 패널 빌더 ────────────────────────────────────────────────
def _threshold_steps(thresholds):
    steps = [{"color": "green", "value": None}]
    if thresholds:
        for val, col in thresholds:
            steps.append({"color": col, "value": val})
    return steps


def stat_panel(pid, title, measurement, unit, color, gridpos,
               description="", thresholds=None, decimals=2):
    """상단 숫자 패널: 현재값(lastNotNull)을 크게 표시, colorMode=background"""
    return {
        "id": pid,
        "type": "stat",
        "title": title,
        "description": description,
        "gridPos": gridpos,
        "datasource": DS,
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "thresholds"},
                "unit": unit,
                "decimals": decimals,
                "thresholds": {
                    "mode": "absolute",
                    "steps": _threshold_steps(thresholds),
                },
                "mappings": [],
                "custom": {},
            },
            "overrides": [],
        },
        "options": {
            "graphMode": "none",
            "colorMode": "background",
            "justifyMode": "center",
            "textMode": "value",
            "orientation": "auto",
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": False,
            },
            "text": {"valueSize": 32},
        },
        "targets": [{"datasource": DS, "query": flux_stat(measurement), "refId": "A"}],
    }


def timeseries_panel(pid, title, measurement, unit, color, gridpos,
                     description="", thresholds=None, decimals=2):
    """하단 그래프 패널: 원래 timeseries 스타일 그대로 유지"""
    return {
        "id": pid,
        "type": "timeseries",
        "title": "",          # 제목은 위 stat 패널에 표시되므로 생략
        "description": description,
        "gridPos": gridpos,
        "datasource": DS,
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "fixed", "fixedColor": color},
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "smooth",
                    "lineWidth": 2,
                    "fillOpacity": 12,
                    "gradientMode": "opacity",
                    "showPoints": "auto",
                    "pointSize": 4,
                    "spanNulls": True,
                    "axisBorderShow": False,
                },
                "unit": unit,
                "decimals": decimals,
                "thresholds": {
                    "mode": "absolute",
                    "steps": _threshold_steps(thresholds),
                },
                "mappings": [],
            },
            "overrides": [],
        },
        "options": {
            "tooltip": {"mode": "single", "sort": "none"},
            "legend": {
                "displayMode": "table",
                "placement": "bottom",
                "showLegend": True,
                "calcs": ["lastNotNull", "min", "max"],
            },
        },
        "targets": [{"datasource": DS, "query": flux_ts(measurement), "refId": "A"}],
    }


def row_panel(pid, title, y):
    return {
        "id": pid,
        "type": "row",
        "title": title,
        "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "panels": [],
    }


def indicator_pair(pid_stat, pid_ts, title, measurement, unit, color,
                   x, y, w, description="", thresholds=None, decimals=2):
    """stat(상단) + timeseries(하단) 쌍 반환"""
    return [
        stat_panel(
            pid_stat, title, measurement, unit, color,
            {"h": STAT_H, "w": w, "x": x, "y": y},
            description, thresholds, decimals,
        ),
        timeseries_panel(
            pid_ts, title, measurement, unit, color,
            {"h": TS_H, "w": w, "x": x, "y": y + STAT_H},
            description, thresholds, decimals,
        ),
    ]


# ── 패널 정의 ─────────────────────────────────────────────────
panels = []

# ════════════════════════════════════════════════
# 버블 신호 섹션
# ════════════════════════════════════════════════
panels.append(row_panel(200, "🔴 버블 신호 (7대 위험 지표)", y=0))

# --- Row 1: 버핏, 쉴러, 공포탐욕, 신용융자 (y=1) ---
#   stat:        y=1,  h=3
#   timeseries:  y=4,  h=9  →  total bottom = 13
ROW1_Y = 1
for pid_s, pid_t, title, meas, unit, color, x, w, desc, thresh in [
    (1,  101, "① 버핏 지수 (Buffett Indicator)",
     "buffett_indicator", "percent", "#F2495C", 0, 6,
     "시총 ÷ GDP × 100. 적정 75-90%, 위험 ≥120%, 현재 ~230%",
     [(120, "yellow"), (200, "red")]),

    (2,  102, "② 쉴러 PER (CAPE Ratio)",
     "shiller_cape", "none", "#FF9830", 6, 6,
     "물가 보정 10년 평균 PER. 역사 평균 17.7배, 현재 ~40배",
     [(25, "yellow"), (35, "red")]),

    (3,  103, "③ 공포 탐욕 지수 (Fear & Greed)",
     "fear_greed_index", "none", "#FADE2A", 12, 6,
     "CNN 심리지표 (0=공포, 100=탐욕). 한 달 만에 27→69",
     [(70, "orange"), (85, "red")]),

    (4,  104, "④ 신용융자 잔고 (Margin Debt, B$)",
     "margin_debt", "short", "#F2495C", 18, 6,
     "빚내서 투자하는 금액 (십억 달러). 전년比 +38.7%",
     [(900, "yellow"), (1100, "red")]),
]:
    panels.extend(indicator_pair(pid_s, pid_t, title, meas, unit, color,
                                  x, ROW1_Y, w, desc, thresh))

# --- Row 2: M7, 버크셔, NVDA (y=13) ---
#   stat: y=13, h=3 / timeseries: y=16, h=9  → bottom=25
ROW2_Y = ROW1_Y + STAT_H + TS_H   # = 1 + 3 + 9 = 13
for pid_s, pid_t, title, meas, unit, color, x, w, desc, thresh in [
    (5,  105, "⑤ 매그니피센트 7 집중도",
     "mag7_concentration", "percent", "#FF780A", 0, 8,
     "M7이 S&P 500에서 차지하는 비중. 현재 33.7% (2016년 12.5%의 3배)",
     [(20, "yellow"), (30, "red")]),

    (6,  106, "⑥ 버크셔 현금 (B$)",
     "berkshire_cash", "short", "#FF4D4D", 8, 8,
     "버크셔 현금+단기국채. 현재 ~3,970억 달러 (~540조원)",
     None),

    (7,  107, "⑦ AI 순환거래 (NVDA 분기매출, B$)",
     "nvda_revenue", "short", "#E02F44", 16, 8,
     "엔비디아 분기 매출 (십억 달러). AI 자금 순환 proxy",
     None),
]:
    panels.extend(indicator_pair(pid_s, pid_t, title, meas, unit, color,
                                  x, ROW2_Y, w, desc, thresh))

# ════════════════════════════════════════════════
# 정상 신호 섹션
# ════════════════════════════════════════════════
ROW3_HEADER_Y = ROW2_Y + STAT_H + TS_H   # = 13 + 3 + 9 = 25
panels.append(row_panel(201, "🟢 정상 신호 (5대 반론 지표)", y=ROW3_HEADER_Y))

# --- Row 3: 동일가중PER, 이익성장, 빅테크현금, GDP (y=26) ---
ROW3_Y = ROW3_HEADER_Y + 1   # = 26
for pid_s, pid_t, title, meas, unit, color, x, w, desc, thresh in [
    (8,  108, "⑧ S&P 500 동일가중 선행 PER",
     "sp500_equal_weight_per", "none", "#3CBC8D", 0, 6,
     "M7 왜곡 제거 후 PER. 현재 ~17배 = 10년 평균 수준",
     [(22, "yellow"), (28, "red")]),

    (9,  109, "⑨ S&P 500 이익 성장률 (YoY %)",
     "sp500_eps_growth", "percent", "#73BF69", 6, 6,
     "6분기 연속 두 자릿수 성장. 2026 Q1: 15.1%",
     None),

    (10, 110, "⑩ 빅테크 현금 (M7 합산, B$)",
     "bigtech_cash", "short", "#5794F2", 12, 6,
     "M7 현금+단기투자 합산. 현재 5,000억+ 달러",
     None),

    (11, 111, "⑪ 미국 실질 GDP 성장률 (YoY %)",
     "us_gdp_growth", "percent", "#37872D", 18, 6,
     "FRED GDPC1. 2026 Q1: +2.0%. AI 투자가 생산성으로 연결",
     None),
]:
    panels.extend(indicator_pair(pid_s, pid_t, title, meas, unit, color,
                                  x, ROW3_Y, w, desc, thresh))

# --- Row 4: S&P 500 지수 전폭 (y=38) ---
ROW4_Y = ROW3_Y + STAT_H + TS_H   # = 26 + 3 + 9 = 38
panels.extend(indicator_pair(
    12, 112,
    "⑫ S&P 500 지수 (참조)",
    "sp500_index", "short", "#8AB8FF",
    0, ROW4_Y, 24,
    "S&P 500 지수 추이. 모든 버블·정상 지표의 맥락 참조용",
    None,
))

# ── 대시보드 정의 ─────────────────────────────────────────────
dashboard = {
    "annotations": {"list": []},
    "description": "너굴경제 영상(https://youtu.be/35B8iC2KD8U) 기반 미국 주식시장 버블 판단 12개 지표 대시보드",
    "editable": True,
    "fiscalYearStartMonth": 0,
    "graphTooltip": 1,
    "id": None,
    "links": [
        {
            "title": "출처 영상 (너굴경제)",
            "url": "https://www.youtube.com/watch?v=35B8iC2KD8U",
            "type": "link",
            "targetBlank": True,
            "icon": "external link",
        }
    ],
    "panels": panels,
    "refresh": "1h",
    "schemaVersion": 39,
    "tags": ["macro", "bubble", "US-market", "너굴경제"],
    "templating": {"list": []},
    "time": {"from": "now-3y", "to": "now"},
    "timepicker": {},
    "timezone": "Asia/Seoul",
    "title": "매크로 버블 지표 대시보드",
    "uid": "macro-bubble-dashboard-v1",
    "version": 3,
}

if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).parent.parent / "grafana" / "dashboards" / "macro_bubble_indicators.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)
    print(f"✅ 생성 완료: {out}")
    print(f"   총 패널 수: {len(panels)} (stat×12 + timeseries×12 + row×2)")
