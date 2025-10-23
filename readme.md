# 📊 AI Trend Forecast Agent (2025–2030)
본 프로젝트는 **SK AX의 AI 서비스 전략 수립**을 지원하기 위해,  
기술·시장 데이터를 통합 분석하고 **향후 5년간 유망한 B2B AI 트렌드 5대 키워드**를 자동 도출하는 LangGraph 기반 멀티-에이전트 시스템입니다.

---

## 🚀 Overview

- **Objective**:  
  전 세계 AI 기술·시장 데이터를 기반으로 *“왜 이 트렌드가 부상하는가”*를 분석하고,  
  SK AX가 진입 가능한 **B2B AI 서비스 기획 영역**을 도출

- **Method**:  
  - LangGraph 기반 **Multi-Agent Orchestration**  
  - RAG 기반 문학·정책 근거 강화 (OECD/IMF 등 PDF)
  - 사업별 시장 수요 + 기술 성졵도 + B2B 적합도 통합 스코어링

- **Tools**:  
  Tavily API, arXiv, GitHub, Google Trends, OpenAI GPT-4o-mini, HuggingFace Embeddings, Chroma

---

## 🧠 Features

- **데이터 수집 자동화**: 논문·GitHub·트렌드·시장 리포트 일괄 수집  
- **기술 성졵도 분석**: 논문·코드 활성도를 기반으로 점수화  
- **시장 수요 분석**: TAM, CAGR, 정보 지원 등으로 기획도 계산  
- **RAG 기반 인사이트**: OECD·IMF 문서에서 국제 AI 정책 매칭 추출  
- **Top 5 트렌드 보고서 생성**: PDF 자동 변환 및 시각화 포함  

---

## 🧹 Architecture

### 🔹 Workflow 구성
```
flowchart TD
    %% ===== Nodes =====
    START([START])
    A1["Agent 1: 데이터 수집"]
    A2["Agent 2: 기술 트렌드 분석"]
    A3["Agent 3: 시장 수요 분석"]
    A4["Agent 4: RAG 기반 통합 분석"]
    A5["Agent 5: 트렌드 교차 분석"]
    A6[["Agent 6: 트렌드 보고서 작성"]]
    END(["최종 보고서 출력"])

    %% ===== Flow =====
    START --> A1
    A1 -->|"논문·GitHub·투자·검색량"| A2
    A1 -->|"시장 리포트·정책 문서"| A3
    A2 -->|"기술별 인사이트"| A4
    A3 -->|"시장별 인사이트"| A4
    A4 -->|"통합 RAG 결과"| A5
    A5 -->|"5대 트렌드 + 기회 점수"| A6
    A6 --> END

    %% ===== Parallel Group (시각적 묶음) =====
    subgraph "병렬 분석"
        direction LR
        A2
        A3
    end

    %% ===== Styles =====
    classDef startStyle fill:#e1f5ff,stroke:#29b6f6,stroke-width:1px,color:#01579b
    classDef endStyle fill:#c8e6c9,stroke:#43a047,stroke-width:1px,color:#1b5e20
    classDef collect fill:#fff9c4,stroke:#fbc02d,color:#795548
    classDef analyze fill:#ffe0b2,stroke:#ff9800,color:#4e342e
    classDef rag fill:#d1c4e9,stroke:#7e57c2,color:#311b92
    classDef cross fill:#ffccbc,stroke:#ff7043,color:#4e342e
    classDef report fill:#f8bbd0,stroke:#ec407a,color:#4a148c

    class START startStyle
    class END endStyle
    class A1 collect
    class A2,A3 analyze
    class A4 rag
    class A5 cross
    class A6 report

```

### 🔹 Graph Framework
- **Framework** : LangGraph + LangChain  
- **Checkpoint** : SQLite Saver (중단 → 재개 가능)  
- **LLM** : OpenAI GPT-4o-mini  
- **Embedding & Retrieval** : HuggingFace MiniLM + Chroma Vectorstore  

---

## 🥮 Evaluation Criteria (SK AX 맞춤형)

| 항목 | 비중 | 설명 |
|------|------|------|
| **기술 성졵도** | 20 % | 논문 활성도 + GitHub 활동성 → 상용화 가능성 |
| **시장 기획도** | 25 % | TAM · CAGR · 정보 지원 정책 |
| **B2B 적합성** | 25 % | 기업 도입률 · 사업별 수요 · ROI 지표 |
| **경쟁 강도** | 15 % | 경쟁자 미일지도 · 진입 장발 (기획 해서 포함) |


> 📌 **RAG 근거 강화 단계**
> - RAG-1 : B2B 도입 사례 / 규제 시그널 보강  
> - RAG-2 : Top 5 선정 이유 및 근거 요약 (Executive Summary 삽입)

---

## ⚙️ Tech Stack

| Category | Details |
|-----------|----------|
| **Framework** | LangGraph, LangChain, Python 3.11 |
| **LLM** | OpenAI GPT-4o-mini |
| **Retrieval** | Chroma + HuggingFace Embeddings |
| **Vectorstore Size** | ~5 MB (사전 인덱싱 OECD 7 IMF PDF) |
| **Visualization** | Matplotlib (Trend Score Charts) |
| **Environment** | Poetry Virtualenv / Windows 11 / Python 3.11 |

---

## 🧱 Agents (노드별 역할)

| Agent | 역할 |
|-------|------|
| **Collector** | arXiv 논문 + GitHub Repo + Google Trends 데이터 수집 |
| **Tech Analyzer** | 논문/Repo 비율로 기술 성졵도 산정 |
| **Market Analyzer** | Tavily 리포트 + 사전 시장 데이터로 기획 점수 계산 |
| **RAG Analyzer** | OECD/IMF PDF RAG 기반 국제 인사이트 추출 |
| **Cross Analyzer** | 기술 × 시장 매칭 후 B2B · AX 가중치 적용 |
| **Report Writer** | Top 5 트렌드 + PDF 보고서 생성 및 시각화 |

---

## 📂 Directory Structure

```
ai_trends_2030/
├── config/
│   ├── settings.py         # 환경 및 API 키 설정
│   ├── keywords.py         # 검색 키워드 및 맵핑
├── tools/
│   ├── arxiv_tool.py       # 논문 검색
│   ├── github_tool.py      # 코드 저장소 검색
│   ├── trends_tool.py      # Google Trends 수집
│   ├── market_tool.py      # Tavily 시장 리포트
│   └── rag_tool.py         # OECD/IMF RAG 분석
├── nodes/
│   ├── collector_node.py   # Agent 1
│   ├── tech_node.py        # Agent 2
│   ├── market_node.py      # Agent 3
│   ├── rag_node.py         # Agent 4
│   ├── cross_node.py       # Agent 5
│   └── report_node.py      # Agent 6
├── graph/workflow.py       # Workflow 빌드 및 시각화
├── outputs/reports/        # 자동 생성 Markdown 및 PDF
├── scripts/test_report.py  # 보고서 단위 테스트
└── main.py                 # 엔드-해-엔드 실행
```

---

## 🧭 B2B Trend Selection Logic

1️⃣ **정량 분석** – arXiv + GitHub + Tavily 데이터로 기술/시장 스코어링  
2️⃣ **RAG 근거 보강** – OECD 7 IMF 리포트 내 정책·투자 매칭 추출  
3️⃣ **B2B 적합성 가중치** – 도입률 · ROI · 사업 연관성 산정  
4️⃣ **중복 클러스터 정리** – LLM/Agent 등 테마 단위로 통합  
5️⃣ **Top 5 도출 + 근거 설명** – “왜 이 5개인가” 를 PDF 에 기록

---

## 🧻 Output Example

- **AI TRENDS 2025-2030.pdf**
  - 표지 + 분석기간 + 작성자
  - Executive Summary (5대 트렌드 요약)
  - Part II: 기술×시장 세부 분석
  - “왜 이 5개인가” (선정 이유 및 RAG 근거)
  - References + Appendix  

---

## 👥 Contributors

| 이름 | 역할 |
|------|------|
| **백광운** | 프로젝트 리드, LangGraph 파이프라인 설계, RAG 분석, 보고서 자동화 |
| **ChatGPT,Claude** | 코드 리팩토링, SK AX 전략 정합성 모델링, README 정리 |
