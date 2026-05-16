# 📊 매크로 버블 지표 대시보드

> 너굴경제 유튜브 영상 **"이거 버블 맞다 vs 이번엔 다르다"** 기반  
> 미국 주식시장 버블 여부를 판단하는 12개 지표를 한눈에 보는 Grafana 대시보드

🎬 **원본 영상**: [https://youtu.be/35B8iC2KD8U](https://www.youtube.com/watch?v=35B8iC2KD8U&list=PLIk4JNQzz-mTDPDdKQ7St2mM-0GC7w82Q)  
📅 영상 업로드: 2026-05-15 | 채널: 너굴경제

---

## 📋 12개 지표 목록

### 🔴 버블 신호 — 7대 위험 지표

| # | 지표 | 현재값 (영상 기준) | 위험 기준 |
|---|------|----------|---------|
| 1 | **버핏 지수** (Buffett Indicator) | **230%** | ≥120% 위험, ≥200% 극단 |
| 2 | **쉴러 PER** (Shiller CAPE) | **40배 이상** | 역사 평균 17.7배 |
| 3 | **공포 탐욕 지수** (CNN Fear & Greed) | **69** (한달 전 27→) | ≥75 극도 탐욕 |
| 4 | **신용융자 잔고** (Margin Debt) | **1.2조 달러** (+38.7% YoY) | 급격한 증가 시 위험 |
| 5 | **매그니피센트 7 집중도** | **33.7%** (2016년 12.5%) | 소수 종목 쏠림 위험 |
| 6 | **버크셔 현금 보유** | **3,970억 달러** (~540조원) | 역사적 최고치 = 신호 |
| 7 | **AI 순환거래 지수** (NVDA 매출 proxy) | 분기 ~52B 달러 | 엔비디아↔AI사 자금 순환 |

### 🟢 정상 신호 — 5대 반론 지표

| # | 지표 | 현재값 (영상 기준) | 해석 |
|---|------|----------|------|
| 8  | **S&P 500 동일가중 선행 PER** | **~17배** | 10년 평균 수준 (M7 왜곡 제거) |
| 9  | **S&P 500 이익 성장률** | **15.1%** (2026 Q1) | 6분기 연속 두 자릿수 성장 |
| 10 | **빅테크 현금 보유** | **5,000억+ 달러** | 부채 아닌 자기자본으로 투자 |
| 11 | **미국 실질 GDP 성장률** | **2.0%** (2026 Q1) | AI 투자가 생산성으로 연결 |
| 12 | **S&P 500 지수** | ~5,600 pts | 종합 참조 |

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────┐
│                  Docker Compose                  │
│                                                 │
│  ┌───────────────┐    ┌─────────────────────┐   │
│  │  data-        │    │     InfluxDB 2.7     │   │
│  │  collector    │───▶│  (시계열 DB)         │   │
│  │  (Python)     │    │  port: 8086          │   │
│  └───────────────┘    └──────────┬──────────┘   │
│                                  │               │
│                       ┌──────────▼──────────┐   │
│                       │   Grafana 10.4       │   │
│                       │   (대시보드)          │   │
│                       │   port: 3000         │   │
│                       └─────────────────────┘   │
└─────────────────────────────────────────────────┘
```

**데이터 흐름:**
1. `collector` 컨테이너가 외부 API(FRED, yfinance, CNN)로부터 3년치 데이터 수집
2. InfluxDB에 time-series 포맷으로 저장
3. Grafana가 InfluxDB를 datasource로 연결, Flux 쿼리로 12개 패널 렌더링

---

## 🚀 빠른 시작

### 사전 요구사항

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Docker Engine + Compose)

### 실행

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/stockdashbaord.git
cd stockdashbaord

# 2. 환경변수 설정
cp .env.example .env
# (선택) .env 파일에서 FRED_API_KEY 설정 가능

# 3. 전체 실행 (InfluxDB + Grafana + 데이터 수집)
docker compose up -d

# 4. 브라우저에서 대시보드 열기
open http://localhost:3000
# 초기 로그인: admin / admin123
```

### 데이터 갱신

```bash
# 수집기 재실행으로 최신 데이터 갱신
docker compose up collector --force-recreate
```

### 종료

```bash
docker compose down           # 컨테이너만 종료 (데이터 보존)
docker compose down -v        # 데이터 볼륨까지 삭제
```

---

## 📊 대시보드 접속 정보

| 서비스 | URL | 기본 계정 |
|--------|-----|---------|
| Grafana | http://localhost:3000 | admin / admin123 |
| InfluxDB | http://localhost:8086 | admin / admin123456 |

> `.env` 파일에서 비밀번호 변경 권장

---

## 🗂️ 프로젝트 구조

```
stockdashbaord/
├── docker-compose.yml              # 전체 서비스 정의
├── .env.example                    # 환경변수 템플릿
├── .env                            # 실제 환경변수 (git 제외)
├── outline.md                      # 프로젝트 기획서
│
├── data-collector/
│   ├── Dockerfile                  # Python 수집기 이미지
│   ├── requirements.txt            # Python 의존성
│   ├── collect.py                  # 12개 지표 수집 메인 스크립트
│   └── generate_dashboard.py       # Grafana 대시보드 JSON 생성기
│
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── influxdb.yml        # InfluxDB datasource 자동 설정
    │   └── dashboards/
    │       └── dashboards.yml      # 대시보드 폴더 설정
    └── dashboards/
        └── macro_bubble_indicators.json  # 12패널 대시보드 정의
```

---

## 📡 데이터 소스

| 지표 | 1차 소스 | Fallback |
|------|---------|---------|
| 버핏 지수 | FRED (WILL5000INDFC + GDP) | 앵커값 기반 추정 |
| 쉴러 PER | [multpl.com](https://www.multpl.com/shiller-pe/table/by-month) | 앵커값 기반 추정 |
| 공포 탐욕 | [CNN Fear & Greed API](https://production.dataviz.cnn.io/index/fearandgreed/graphdata/) | 앵커값 기반 추정 |
| 신용융자 잔고 | [FINRA 통계](https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics) | 앵커값 기반 추정 |
| M7 집중도 | yfinance (AAPL/MSFT/GOOGL/AMZN/META/NVDA/TSLA) | 앵커값 기반 추정 |
| 버크셔 현금 | yfinance (BRK-B 분기 재무제표) | 공개 분기 데이터 |
| NVDA 매출 | yfinance 분기 실적 | 공개 분기 데이터 |
| 동일가중 PER | yfinance (RSP ETF) | 앵커값 기반 추정 |
| S&P 500 이익 성장률 | 공개 실적 데이터 | - |
| 빅테크 현금 | yfinance (M7 재무제표 합산) | 앵커값 기반 추정 |
| GDP 성장률 | FRED (GDPC1) | 앵커값 기반 추정 |
| S&P 500 지수 | yfinance (^GSPC) | 앵커값 기반 추정 |

> **Fallback**: 외부 API 접근 실패 시 영상 기준 앵커값과 3년 추정 데이터를 사용합니다.  
> 실제 데이터 확보를 위해 컨테이너 외부에서 수집기를 직접 실행하거나 FRED API 키를 설정하세요.

---

## 🔧 다른 시스템으로 이식 (포팅 가이드)

### 클라우드 환경 (AWS / GCP / Azure)

```bash
# 1. 도커 이미지 레지스트리에 push
docker tag stockdashbaord-collector your-registry/macro-collector:latest
docker push your-registry/macro-collector:latest

# 2. docker-compose.yml의 image 필드를 레지스트리 주소로 변경
# 3. 클라우드 환경에서 동일하게 docker compose up -d
```

### 환경변수 커스터마이징

`.env` 파일만 수정하면 모든 비밀번호·설정 변경 가능:

```env
INFLUXDB_TOKEN=your-secure-token-here
GF_ADMIN_PASSWORD=your-secure-password
FRED_API_KEY=your-fred-api-key    # https://fred.stlouisfed.org/docs/api/api_key.html
```

### Grafana 대시보드 재생성

지표나 레이아웃 변경 시:

```bash
python3 data-collector/generate_dashboard.py
docker compose restart grafana
```

### InfluxDB 직접 쿼리 (Flux)

```flux
from(bucket: "macro_indicators")
  |> range(start: -3y)
  |> filter(fn: (r) => r["_measurement"] == "buffett_indicator")
  |> filter(fn: (r) => r["_field"] == "value")
```

사용 가능한 `_measurement` 값:
`buffett_indicator`, `shiller_cape`, `fear_greed_index`, `margin_debt`,
`mag7_concentration`, `berkshire_cash`, `nvda_revenue`,
`sp500_equal_weight_per`, `sp500_eps_growth`, `bigtech_cash`,
`us_gdp_growth`, `sp500_index`

---

## ⚠️ 면책 사항

이 대시보드는 **교육·학습 목적**으로 제작되었습니다.  
영상 기준 앵커값과 추정 데이터가 포함되어 있으며, 실제 투자 결정에 사용하지 마세요.

---

## 📄 라이선스

MIT License
