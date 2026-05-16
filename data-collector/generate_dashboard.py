#!/usr/bin/env python3
"""Grafana 대시보드 JSON 생성기"""
import json

DS = {"type": "influxdb", "uid": "macro-influxdb"}

def flux(measurement: str) -> str:
    return (
        f'from(bucket: "macro_indicators")\n'
        f'  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n'
        f'  |> filter(fn: (r) => r["_measurement"] == "{measurement}")\n'
        f'  |> filter(fn: (r) => r["_field"] == "value")\n'
        f'  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\n'
        f'  |> yield(name: "mean")'
    )

def timeseries_panel(pid, title, measurement, unit, color, gridpos,
                     description="", thresholds=None, decimals=2):
    threshold_steps = [{"color": "green", "value": None}]
    if thresholds:
        for val, col in thresholds:
            threshold_steps.append({"color": col, "value": val})

    return {
        "id": pid,
        "type": "timeseries",
        "title": title,
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
                    "steps": threshold_steps,
                },
                "mappings": [],
            },
            "overrides": [],
        },
        "options": {
            "tooltip": {"mode": "single", "sort": "none"},
            "legend": {
                "displayMode": "list",
                "placement": "bottom",
                "showLegend": True,
                "calcs": ["lastNotNull", "min", "max"],
            },
        },
        "targets": [
            {
                "datasource": DS,
                "query": flux(measurement),
                "refId": "A",
            }
        ],
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

panels = []

# ── 버블 신호 행 헤더 ─────────────────────────────────────
panels.append(row_panel(100, "🔴 버블 신호 (7대 위험 지표)", y=0))

# Row 1 (y=1): 버핏, 쉴러, 공포탐욕, 신용융자
row1_defs = [
    (1,  "① 버핏 지수 (Buffett Indicator)",
     "buffett_indicator", "percent", "#F2495C",
     {"gridPos": {"h": 9, "w": 6, "x": 0,  "y": 1}},
     "워런 버핏이 '가장 좋은 단일 지표'라고 언급. 미국 주식시장 시총 ÷ GDP × 100. 현재 ~230% (적정 75-90%, 위험 ≥120%)",
     [(120, "yellow"), (200, "red")]),

    (2,  "② 쉴러 PER (CAPE Ratio)",
     "shiller_cape", "none", "#FF9830",
     {"gridPos": {"h": 9, "w": 6, "x": 6,  "y": 1}},
     "물가 보정 10년 평균 실적 기준 PER. 역사적 평균 17.7배. 현재 ~40배 (역대 2위, 1위=닷컴버블 44.2배)",
     [(25, "yellow"), (35, "red")]),

    (3,  "③ 공포 탐욕 지수 (Fear & Greed)",
     "fear_greed_index", "none", "#FADE2A",
     {"gridPos": {"h": 9, "w": 6, "x": 12, "y": 1}},
     "CNN 제작 단기 심리 지표 (0=극도 공포, 100=극도 탐욕). 한 달 만에 27→69 급등",
     [(70, "orange"), (85, "red")]),

    (4,  "④ 신용융자 잔고 (Margin Debt)",
     "margin_debt", "short", "#F2495C",
     {"gridPos": {"h": 9, "w": 6, "x": 18, "y": 1}},
     "빚내서 투자하는 금액 (십억 달러). 현재 ~1.2조 달러, 전년比 +38.7%. 하락 시 마진콜 → 폭락 가속 위험",
     [(900, "yellow"), (1100, "red")]),
]
for pid, title, meas, unit, color, extra, desc, thresh in row1_defs:
    gp = extra["gridPos"]
    panels.append(timeseries_panel(pid, title, meas, unit, color, gp, desc, thresh))

# Row 2 (y=10): M7, 버크셔, NVDA
row2_defs = [
    (5,  "⑤ 매그니피센트 7 집중도",
     "mag7_concentration", "percent", "#FF780A",
     {"h": 9, "w": 8, "x": 0,  "y": 10},
     "애플·MS·구글·아마존·메타·엔비디아·테슬라 7개사가 S&P 500에서 차지하는 비중. 현재 33.7% (2016년 12.5%에서 3배 증가)",
     [(20, "yellow"), (30, "red")]),

    (6,  "⑥ 버크셔 해서웨이 현금",
     "berkshire_cash", "short", "#FF4D4D",
     {"h": 9, "w": 8, "x": 8,  "y": 10},
     "버크셔 현금+단기국채 보유액 (십억 달러). 현재 ~3,970억 달러 (약 540조원). 닷컴버블·서브프라임 직전과 유사한 패턴",
     None),

    (7,  "⑦ AI 순환거래 지수 (NVDA 분기 매출 proxy)",
     "nvda_revenue", "short", "#E02F44",
     {"h": 9, "w": 8, "x": 16, "y": 10},
     "엔비디아 분기 매출 (십억 달러). AI 기업간 자금 순환의 핵심 proxy. 현재 분기 매출 ~52B",
     None),
]
for pid, title, meas, unit, color, gp, desc, thresh in row2_defs:
    panels.append(timeseries_panel(pid, title, meas, unit, color, gp, desc, thresh))

# ── 정상 신호 행 헤더 ─────────────────────────────────────
panels.append(row_panel(101, "🟢 정상 신호 (5대 반론 지표)", y=19))

# Row 3 (y=20): 동일가중PER, 이익성장, 빅테크현금, GDP
row3_defs = [
    (8,  "⑧ S&P 500 동일가중 선행 PER",
     "sp500_equal_weight_per", "none", "#3CBC8D",
     {"h": 9, "w": 6, "x": 0,  "y": 20},
     "매그니피센트 7 왜곡 제거 후 PER. 현재 ~17배 = 10년 평균 수준. '나머지 493개 기업은 정상 가격'",
     [(22, "yellow"), (28, "red")]),

    (9,  "⑨ S&P 500 이익 성장률 (YoY %)",
     "sp500_eps_growth", "percent", "#73BF69",
     {"h": 9, "w": 6, "x": 6,  "y": 20},
     "S&P 500 기업 분기 이익 성장률. 6분기 연속 두 자릿수 성장. 2026 Q1: 15.1% (예상 10% 상회)",
     None),

    (10, "⑩ 빅테크 현금 보유 (M7 합산)",
     "bigtech_cash", "short", "#5794F2",
     {"h": 9, "w": 6, "x": 12, "y": 20},
     "매그니피센트 7 현금+단기투자 합산 (십억 달러). 현재 5,000억 달러 이상. 부채가 아닌 자기자본으로 AI 인프라 투자",
     None),

    (11, "⑪ 미국 실질 GDP 성장률 (YoY %)",
     "us_gdp_growth", "percent", "#37872D",
     {"h": 9, "w": 6, "x": 18, "y": 20},
     "FRED GDPC1 기준 실질 GDP 전년비 성장률. 2026 Q1: +2.0%. AI 투자가 거시경제 생산성으로 연결되는 신호",
     None),
]
for pid, title, meas, unit, color, gp, desc, thresh in row3_defs:
    panels.append(timeseries_panel(pid, title, meas, unit, color, gp, desc, thresh))

# Row 4 (y=29): S&P 500 지수 (전폭)
panels.append(timeseries_panel(
    12, "⑫ S&P 500 지수 (참조)",
    "sp500_index", "short", "#8AB8FF",
    {"h": 9, "w": 24, "x": 0, "y": 29},
    "S&P 500 지수 추이. 모든 버블·정상 지표의 맥락 참조용",
    None,
))

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
    "version": 1,
}

if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).parent.parent / "grafana" / "dashboards" / "macro_bubble_indicators.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)
    print(f"✅ 생성: {out}")
