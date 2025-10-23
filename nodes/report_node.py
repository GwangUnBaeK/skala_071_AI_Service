# nodes/report_node.py
"""
최종 보고서 생성 노드
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from config.settings import settings
from utils.logger import logger
from datetime import datetime

def report_generation_node(state: GraphState):
    """최종 보고서 생성 (PDF만)"""
    logger.info("="*70)
    logger.info("📝 Agent 6: 최종 보고서 생성 (PDF)")
    logger.info("="*70)
    
    llm = ChatOpenAI(
        model=settings.LLM["model"],
        temperature=settings.LLM["temperature"]
    )
    
    top_5_trends = state.get("top_5_trends", [])
    
    if not top_5_trends:
        logger.error("❌ Top 5 트렌드가 없습니다!")
        return {
            "final_report": "오류: Top 5 트렌드 데이터가 없습니다.",
            "step_report": "failed"
        }
    
    # 1️⃣ 커버 페이지 생성
    logger.info("1️⃣ 커버 페이지 생성 중...")
    cover_page = generate_cover_page(top_5_trends, state)
    
    # 2️⃣ Executive Summary
    logger.info("2️⃣ Executive Summary 생성 중...")
    executive_summary = generate_executive_summary(top_5_trends, llm)
    
    # 3️⃣ Top 5 한눈에 보기
    logger.info("3️⃣ Top 5 요약 생성 중...")
    top_5_summary = generate_top5_summary(top_5_trends)
    
    # 4️⃣ 분석 방법론
    logger.info("4️⃣ 분석 방법론 생성 중...")
    methodology = generate_methodology(state)
    
    # 5️⃣ 각 트렌드 상세 내용
    logger.info("5️⃣ 트렌드 상세 내용 생성 중...")
    trend_details = []
    for idx, trend in enumerate(top_5_trends, 1):
        logger.info(f"   [{idx}/5] '{trend['trend_keyword']}' 상세 내용 생성 중...")
        try:
            detail = generate_trend_detail(trend, llm)

            if idx > 1:
                detail = f'\n\n<div style="page-break-before: always;"></div>\n\n{detail}'
                
            trend_details.append(detail)
            logger.info(f"      ✓ 완료 ({len(detail):,}자)")
        except Exception as e:
            logger.error(f"      ✗ 실패: {e}")
            trend_details.append(f"## {idx}. {trend['trend_keyword']}\n\n상세 내용 생성 실패\n\n")
    
    # 6️⃣ SK AX 전략 제언
    logger.info("6️⃣ SK AX 전략 제언 생성 중...")
    strategy = generate_strategy_top1(top_5_trends, llm)
    
    # 7️⃣ References
    logger.info("7️⃣ References 생성 중...")
    references = generate_references(state)
    
    # 8️⃣ Appendix
    logger.info("8️⃣ Appendix 생성 중...")
    appendix = generate_appendix()
    
    # 전체 보고서 조립
    report = f"""# AI TRENDS 2025-2030

{cover_page}

---

{executive_summary}

---

{top_5_summary}

---

{methodology}

---

# PART 2. 5대 트렌드 상세 분석

각 트렌드는 4-5페이지 분량으로 구성되어 있습니다.

---

{''.join(trend_details)}

---

{strategy}

---

{references}

---

{appendix}
"""
    
    # ✅ PDF만 생성 (Markdown 저장 안 함)
    output_dir = "outputs/reports"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"{output_dir}/AI_TRENDS_{timestamp}.pdf"
    
    # PDF 변환 (Markdown 파일 없이 바로 생성)
    try:
        logger.info(f"📄 PDF 생성 중...")
        convert_md_to_pdf_direct(report, pdf_filename)
        logger.info(f"✅ PDF 저장: {pdf_filename}\n")
    except Exception as e:
        logger.error(f"❌ PDF 생성 실패: {e}\n")
        # 실패 시 Markdown이라도 저장
        md_filename = f"{output_dir}/AI_TRENDS_{timestamp}.md"
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"⚠️ Markdown 대체 저장: {md_filename}\n")
    
    return {
        "final_report": report,
        "step_report": "completed"
    }


def generate_cover_page(top_5_trends, state):
    """✅ 커버 페이지 (1페이지 + 2페이지 합침)"""
    
    # 작성자 정보
    author_name = os.getenv("AUTHOR_NAME", "AI Trends Analysis Team")
    
    return f"""5년 후 세상을 바꿀 5대 AI 트렌드

**작성자:** {author_name}  
**보고서 생성일:** {datetime.now().strftime('%Y년 %m월 %d일')}  
**분석 기간:** {settings.ANALYSIS['date_range']['start']} - {settings.ANALYSIS['date_range']['end']}  
**분석 대상:** AI 기술 및 시장
"""


def generate_executive_summary(top_5_trends, llm):
    """Executive Summary 생성"""
    
    trends_summary = "\n".join([
        f"{i}. {t['trend_keyword']}: {t['tech']['tech_name']} × {t['market']['demand_name']} (점수 {t['final_score']:.1f})"
        for i, t in enumerate(top_5_trends, 1)
    ])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 McKinsey 수석 컨설턴트입니다.
        
**중요: 모든 답변은 완벽한 한글로 작성하세요.**

- 경영진용 요약 (1페이지)
- 핵심 메시지 명확
- 구체적 수치 포함
- SK AX 관점 제언"""),
        
        ("human", """다음 Top 5 AI 트렌드를 바탕으로 **Executive Summary**를 작성하세요:

{trends_summary}

---

다음 구조로 작성:

# EXECUTIVE SUMMARY

## Executive Summary

### 핵심 메시지
(2-3문단, 전체 트렌드의 핵심 메시지)

### Top 5 트렌드 요약
(각 트렌드당 3-4줄, 핵심 수치 포함)

1. [트렌드 1]: ...
2. [트렌드 2]: ...
3. [트렌드 3]: ...
4. [트렌드 4]: ...
5. [트렌드 5]: ...

### SK AX를 위한 핵심 제언
(3개, 각 2줄)

1. [제언 1]
2. [제언 2]
3. [제언 3]

### 즉시 실행 가능한 Next Action
(1문단, 구체적 액션)
""")
    ])
    
    response = llm.invoke(prompt.format_messages(trends_summary=trends_summary))
    return response.content


def generate_top5_summary(top_5_trends):
    """Top 5 한눈에 보기"""
    
    summary_lines = []
    for trend in top_5_trends:
        summary_lines.append(f"""**{trend['rank']}. {trend['trend_keyword']} (최종 점수: {trend['final_score']:.1f}/100)**
- 핵심 기술: {trend['tech']['tech_name']} (성숙도 {trend['tech']['maturity_score']:.1f}/100)
- 타겟 시장: {trend['market']['demand_name']} (기회 {trend['market']['opportunity_score']:.1f}/100)
- 시장 규모: TAM ${trend['market']['tam_usd']:,} USD
- 연성장률: {trend['market']['cagr']*100:.1f}% CAGR
- 경쟁 강도: {trend['competition']:.1f}/100
""")
    
    return f"""# 🎯 Top 5 트렌드 한눈에 보기

{chr(10).join(summary_lines)}"""


def generate_methodology(state):
    """분석 방법론"""
    
    papers_count = len(state.get("papers", []))
    github_count = len(state.get("github_repos", []))
    keywords_count = len(state.get("keywords", []))
    
    return f"""# PART 1. 분석 방법론

## 1.1 데이터 소스

- **arXiv 논문:** {papers_count}편 (2023-2025)
- **GitHub 저장소:** {github_count}개 프로젝트
- **Google Trends:** {keywords_count}개 키워드
- **시장 리포트:** Tavily API 실시간 검색
- **전문 문서 (RAG):** OECD PDF, IMF PDF

## 1.2 평가 기준

| 기준 | 가중치 | 설명 |
|------|--------|------|
| 기술 성숙도 | 25% | 논문 대비 제품화 비율, GitHub 활동도 |
| 시장 기회 | 35% | TAM, 타겟 기업 수, 정부 지원 |
| 시장 성장률 | 25% | CAGR (연평균 성장률) |
| 경쟁 강도 | -15% | 빅테크 관심도, 스타트업 경쟁 |

자세한 평가 로직은 부록(APPENDIX) 참조
"""

def generate_trend_detail(trend: dict, llm: ChatOpenAI) -> str:

    """
    ✅ 각 트렌드 상세 내용 생성 (테마 기반)
    - 이제 trend는 "테마"이고, 여러 기술×시장 조합을 포함
    """
    
    # 테마 정보
    theme_name = trend["trend_keyword"]  # "AI Workforce Era"
    
    # 대표 기술 (가장 성숙도 높은 것)
    representative_tech = trend["tech"]
    tech_name = representative_tech["tech_name"]
    
    # 대표 시장 (가장 기회 점수 높은 것)
    representative_market = trend["market"]
    market_name = representative_market["demand_name"]
    
    # 미래 TAM 계산 (대표 시장 기준)
    current_tam = representative_market["tam_usd"]
    cagr = representative_market["cagr"]
    future_tam = int(current_tam * ((1 + cagr) ** 5))
    
    # 🆕 테마에 속한 모든 기술/시장 목록
    all_tech_names = trend["evidence"]["tech_examples"]  # ["LLM agent", "document automation", ...]
    all_market_names = trend["evidence"]["market_examples"]
    
    # RAG 인사이트
    rag_insight = trend.get("rag_insight", {}).get("answer", "전문 문서 분석 없음")
    
    # GitHub 프로젝트
    github_projects = ", ".join(representative_tech.get("related_projects", ["없음"])[:3])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 20년 경력의 기술 트렌드 분석 전문가입니다.

**중요: 보고서는 완벽한 한글로 작성하세요.**

- 영문 논문과 데이터를 참고하되, 모든 설명은 한글로 작성
- 기술 용어는 한글 우선, 필요시 영문 병기 (예: 생성형 AI (Generative AI))
- 기업명, 제품명은 원어 그대로 사용 (예: OpenAI, ChatGPT)
- 자연스럽고 전문적인 한국어 문체 유지
- **리스트는 반드시 줄바꿈**
- **데이터 포인트는 각각 줄바꿈 + 하위 설명**"""),
        
        ("human", """
다음 AI 트렌드 테마에 대해 **한글로 4-5페이지 분량**의 상세 분석을 작성하세요:

**🎯 트렌드 테마:** {theme_name}

**핵심 기술 조합:**
{all_tech_names}

**타겟 시장 조합:**
{all_market_names}

**대표 사례:**
- 대표 기술: {tech_name} (성숙도 {maturity}점/100)
- 대표 시장: {market_name} (기회 {opportunity}점/100)

**시장 데이터:**
- 현재 규모: ${tam:,} USD (2025)
- 미래 예상: ${future_tam:,} USD (2030)
- 연평균 성장률: {cagr:.1f}%
- 경쟁 강도: {competition}점/100

**기술 데이터:**
- 논문 수: {paper_count}편
- GitHub Stars: {github_stars:,}개
- 주요 프로젝트: {github_projects}

**전문 문서 인사이트:**
{rag_insight}

---

다음 구조로 **완벽한 한글**로 작성하세요:

## {theme_name}

### 1. 개요 및 핵심 메시지

**이 트렌드는 무엇인가?**

(2-3문단: {theme_name} 테마의 의미와 왜 중요한지 설명)
- 이 테마는 다음 기술들의 융합입니다: {all_tech_names}
- 다음 시장들을 타겟으로 합니다: {all_market_names}

**2030년 예상 모습:**

(2-3문단: 구체적 시나리오)
- 대표 기업들의 활용 사례
- 일상/업무에서의 변화
- 산업 전반의 혁신

**핵심 데이터 포인트:**

- **종합 점수:** {final_score}점/100
  - 이 테마가 향후 5년간 가장 유망한 이유
  
- **기술 성숙도:** {maturity}점 (대표 기술 기준)
  - {tech_name}을 포함한 {tech_count}개 기술이 상용화 단계 진입
  
- **시장 규모:** ${tam:,} (2025) → ${future_tam:,} (2030)
  - CAGR {cagr:.1f}%, 연평균 성장률이 매우 높음
  
- **경쟁 강도:** {competition}점
  - 빅테크 진입 여부, 스타트업 경쟁 수준 분석

### 2. 기술 배경 및 발전 단계

#### 2.1 기술 융합의 힘

이 테마는 단일 기술이 아닌 **여러 기술의 조합**으로 시너지를 냅니다:

**핵심 기술 1: {tech_name}**
(2문단: 이 기술의 원리와 혁신성)

**관련 기술 조합:**
- {all_tech_names}을(를) 함께 활용하여 강력한 솔루션 구현

#### 2.2 기술 성숙도 분석

**현재 단계:** (연구/베타/얼리어답터/상용화 중 하나)

**근거:**
- 논문: {paper_count}편 (최근 2년간 급증)
- GitHub: {github_stars:,} Stars (활발한 오픈소스 활동)
- 대표 프로젝트: {github_projects}

**대표 기업 및 제품 사례:**

1. [실제 기업명] - [제품명]
   - 활용 기술: {tech_name} 기반
   - 성과: (구체적 수치, 예: 비용 30% 절감)
   - 특징: (차별화 포인트 1줄)

2. [실제 기업명] - [제품명]
   - 활용 기술: (여러 기술 조합 명시)
   - 성과: (구체적 수치)
   - 특징: (1줄)

3. [실제 기업명] - [제품명]
   - 활용 기술: (기술 조합)
   - 성과: (구체적 수치)
   - 특징: (1줄)

### 3. 시장 기회 분석

#### 3.1 다층적 시장 수요

이 테마는 **{market_count}개의 시장 영역**에서 동시다발적 수요가 발생합니다:

**주요 타겟 시장:**
{all_market_names}

**시장별 문제 정의:**

1. {market_name} (대표 시장)
   - 문제: {market_problem}
   - 타겟: {target_companies:,}개 기업
   - 규모: ${tam:,}

2. [두 번째 시장]
   - 문제: (구체적 pain point)
   - 타겟: (고객 규모)
   - 규모: (시장 규모)

#### 3.2 시장 규모 및 성장

**전체 시장 규모 (TAM):**
- 2025년: ${tam:,}
- 2030년: ${future_tam:,}
- CAGR: {cagr:.1f}%

**주요 산업:** {industries}

**지역별 분포:** {regions}

**성장 동력:**
- (3개 이유, 각 2줄)

#### 3.3 실제 적용 사례

**사례 1: [기업명] - {market_name} 시장**
- 도입 배경: (1줄)
- 활용 기술: {tech_name} 등
- 정량적 효과: (예: 생산성 40% 향상, ROI 18개월)
- 핵심 성공 요인: (1줄)

**사례 2: [기업명] - [다른 시장]**
- 도입 배경: (1줄)
- 활용 기술: (기술 조합)
- 정량적 효과: (구체적 수치)
- 핵심 성공 요인: (1줄)

**사례 3: [기업명]**
- (동일 형식)

### 4. 경쟁 환경 분석

#### 4.1 주요 경쟁자

**빅테크 기업:**
- [기업명]: {theme_name} 테마에서의 포지션 (2줄)
- [기업명]: 관련 제품/서비스 (2줄)
- [기업명]: 투자 및 전략 (2줄)

**주목할 스타트업:**
- [스타트업명] (평가액/투자 유치액): 핵심 솔루션 (2줄)
- [스타트업명]: 차별화 포인트 (2줄)
- [스타트업명]: 성장 가능성 (2줄)

**경쟁 강도 평가:** {competition}점/100
- 해석: (2-3줄, 진입 난이도와 전략적 시사점)

#### 4.2 진입 장벽

- **기술적 장벽:** (2줄, {tech_name} 등 핵심 기술 확보 난이도)
- **자본 요구사항:** (2줄, 초기 투자 규모 및 손익분기점)
- **규제 이슈:** (2줄, 관련 법규 및 대응 방안)
- **네트워크 효과:** (2줄, 선발주자 우위 정도)

### 5. SK AX 전략 제언

#### 5.1 왜 이 테마인가?

**전략적 중요성:**
(2-3문단: {theme_name}이 SK AX에게 왜 중요한 기회인지)

- 시장 규모: ${tam:,} → ${future_tam:,} (CAGR {cagr:.1f}%)
- 타겟 고객: {target_companies:,}개 기업
- 기술 성숙도: {maturity}점 (진입 적기)
- 경쟁 강도: {competition}점 (중간 수준, 후발주자 기회 존재)

#### 5.2 진입 전략

**타이밍:**
- 권장 시점: (즉시/6개월/1년 후)
- 근거: (3줄, 기술 성숙도와 시장 상황 고려)

**포지셔닝:**
- 차별화 전략: (3-4줄)
  - 빅테크와의 차별점
  - 타겟 시장 세분화
  - 기술적 우위 확보 방안

**타겟 세그먼트 (우선순위):**
1. {market_name} (1차 타겟)
   - 이유: (2줄)
   - 접근 방법: (2줄)

2. [두 번째 시장] (2차 타겟)
   - 이유: (2줄)
   - 접근 방법: (2줄)

**Go-to-Market 전략:**
- Phase 1 (0-6개월): (구체적 액션 아이템 3개)
- Phase 2 (6-12개월): (확장 전략 3개)
- Phase 3 (1-2년): (스케일업 전략 3개)

---

**작성 원칙:**
- **테마는 여러 기술과 시장의 조합**임을 명확히 표현
- 대표 사례(기술/시장)를 중심으로 설명하되, 전체 조합도 언급
- 모든 리스트는 줄바꿈
- 데이터 포인트는 각각 줄바꿈 + 하위 설명
- 모든 수치는 구체적으로
- 모든 사례는 실명으로 (가상 사례 금지)
- 4-5페이지 분량 (약 3,500-4,500자)
        """)
    ])
    
    response = llm.invoke(prompt.format_messages(
        theme_name=theme_name,
        tech_name=tech_name,
        market_name=market_name,
        all_tech_names="\n".join([f"- {t}" for t in all_tech_names]),
        all_market_names="\n".join([f"- {m}" for m in all_market_names]),
        tech_count=trend["evidence"]["tech_count"],
        market_count=trend["evidence"]["market_count"],
        maturity=representative_tech["maturity_score"],
        opportunity=representative_market["opportunity_score"],
        tam=current_tam,
        future_tam=future_tam,
        cagr=cagr * 100,
        competition=trend["competition"],
        final_score=trend["final_score"],
        paper_count=representative_tech.get("paper_count", 0),
        github_stars=representative_tech.get("github_stars_total", 0),
        github_projects=github_projects,
        target_companies=representative_market.get("target_companies", 0),
        industries=", ".join(representative_market.get("industries", ["다양한 산업"])),
        regions=", ".join(representative_market.get("regions", ["글로벌"])),
        market_problem=representative_market.get("problem_statement", "시장 수요 존재"),
        rag_insight=rag_insight
    ))
    
    return response.content
    """✅ 각 트렌드 상세 내용 생성 (5. SK AX 전략 제언 간소화)"""
    
    # 미래 TAM 계산
    current_tam = trend["market"]["tam_usd"]
    cagr = trend["market"]["cagr"]
    future_tam = int(current_tam * ((1 + cagr) ** 5))
    
    # RAG 인사이트
    rag_insight = trend.get("rag_insight", {}).get("answer", "전문 문서 분석 없음")
    
    # GitHub 프로젝트
    github_projects = ", ".join(trend["tech"].get("related_projects", ["없음"])[:3])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 20년 경력의 기술 트렌드 분석 전문가입니다.

**중요: 보고서는 완벽한 한글로 작성하세요.**

- 영문 논문과 데이터를 참고하되, 모든 설명은 한글로 작성
- 기술 용어는 한글 우선, 필요시 영문 병기 (예: 생성형 AI (Generative AI))
- 기업명, 제품명은 원어 그대로 사용 (예: OpenAI, ChatGPT)
- 자연스럽고 전문적인 한국어 문체 유지
- **리스트는 반드시 줄바꿈**
- **데이터 포인트는 각각 줄바꿈 + 하위 설명**"""),
        
        ("human", """
다음 AI 트렌드에 대해 **한글로 4-5페이지 분량**의 상세 분석을 작성하세요:

**트렌드 제목:** {keyword}
**핵심 기술:** {tech_name} (기술 성숙도 {maturity}점/100)
**타겟 시장:** {market_name} (시장 기회 점수 {opportunity}점/100)
**시장 규모:** TAM ${tam:,} USD (2025) → ${future_tam:,} USD (2030 예상)
**연평균 성장률:** {cagr:.1f}%
**경쟁 강도:** {competition}점/100
**주요 GitHub 프로젝트:** {github_projects}

**전문 문서 인사이트:**
{rag_insight}

---

다음 구조로 **완벽한 한글**로 작성하세요:

## {keyword}

### 1. 개요 및 핵심 메시지

(3-4문단, 핵심 메시지 명확)

**2030년 예상 모습:**

(구체적 시나리오, 2-3문단)

**핵심 데이터 포인트:**

- **기술 성숙도:** {maturity}점
  - (의미 해석, 1줄)
- **시장 규모:** ${{tam:,}} (2025) → ${{future_tam:,}} (2030)
  - (성장률 {cagr:.1f}% 의미, 1줄)
- **경쟁 강도:** {competition}점
  - (진입 난이도 분석, 1줄)

### 2. 기술 배경 및 발전 단계

#### 2.1 기술 설명

(2-3문단, {tech_name} 핵심 원리 및 혁신성)

#### 2.2 기술 성숙도 분석

**현재 단계:** (연구/베타/얼리어답터/상용화 중 하나 선택, 1줄)

**근거:**

- 논문 수: {{paper_count}}편
- GitHub Stars: {{github_stars:,}}개
- 주요 오픈소스 프로젝트: {{github_projects}}

**대표 기업 및 제품 사례:**

1. [실제 기업명] ([제품명]): 사례 설명 (3-4줄, 구체적 효과 포함)
2. [실제 기업명] ([제품명]): 사례 설명 (3-4줄, 구체적 효과 포함)
3. [실제 기업명] ([제품명]): 사례 설명 (3-4줄, 구체적 효과 포함)

### 3. 시장 기회 분석

#### 3.1 시장 수요

**문제 정의:** {{market_problem}}

**타겟 고객:** {{target_companies:,}}개 기업

(2-3문단, 시장 수요 설명)

#### 3.2 시장 규모 및 성장

- **2025년 TAM:** ${{tam:,}}
- **2030년 예상:** ${{future_tam:,}}
- **연평균 성장률:** {{cagr:.1f}}%
- **주요 산업:** {{industries}}
- **지역별 분포:** {{regions}}

#### 3.3 실제 적용 사례

**사례 1: [기업명]**

- 도입 배경 (1줄)
- 효과 (구체적 수치)
- ROI (1줄)

**사례 2: [기업명]**

- 도입 배경 (1줄)
- 효과 (구체적 수치)
- ROI (1줄)

**사례 3: [기업명]**

- 도입 배경 (1줄)
- 효과 (구체적 수치)
- ROI (1줄)

### 4. 경쟁 환경 분석

#### 4.1 주요 경쟁자

**빅테크 기업:**

- [기업명]: 주요 움직임 (1줄)
- [기업명]: 주요 움직임 (1줄)
- [기업명]: 주요 움직임 (1줄)

**주목할 스타트업:**

- [스타트업명]: 핵심 솔루션 (1줄)
- [스타트업명]: 핵심 솔루션 (1줄)
- [스타트업명]: 핵심 솔루션 (1줄)

**경쟁 강도:** {competition}점 → 해석 (1-2줄)

#### 4.2 진입 장벽

- **기술적 장벽:** (1줄)
- **자본 요구사항:** (1줄)
- **규제 이슈:** (1줄)

### 5. SK AX 전략 제언

#### 5.1 시장 기회

(2-3문단, 이 트렌드가 SK AX에게 왜 기회인지)

- 시장 규모: ${{tam:,}} → ${{future_tam:,}} (CAGR {cagr:.1f}%)
- 타겟 고객: {{target_companies:,}}개 기업
- 진입 시점: 현재 기술 성숙도 {maturity}점

#### 5.2 진입 전략

**타이밍:**

- (즉시/6개월/1년 후 선택 + 이유 2줄)

**포지셔닝:**

- (차별화 포인트 3줄)

**타겟 세그먼트:**

- (B2B/B2C, 구체적 고객군 3줄)
         
---

**작성 원칙:**
- 모든 리스트는 줄바꿈
- 데이터 포인트는 각각 줄바꿈 + 하위 설명
- 모든 수치는 구체적으로
- 모든 사례는 실명으로
- 4-5페이지 분량 (약 3,000-4,000자)
- **5.3 예상 성과는 작성하지 말것**         
        """)
    ])
    
    response = llm.invoke(prompt.format_messages(
        rank=trend["rank"],
        keyword=trend["trend_keyword"],
        tech_name=trend["tech"]["tech_name"],
        maturity=trend["tech"]["maturity_score"],
        market_name=trend["market"]["demand_name"],
        market_problem=trend["market"].get("problem_statement", "시장 수요 존재"),
        opportunity=trend["market"]["opportunity_score"],
        tam=current_tam,
        future_tam=future_tam,
        cagr=cagr * 100,
        competition=trend["competition"],
        paper_count=trend["tech"].get("paper_count", 0),
        github_stars=trend["tech"].get("github_stars_total", 0),
        github_projects=github_projects,
        target_companies=trend["market"].get("target_companies", 0),
        industries=", ".join(trend["market"].get("industries", ["다양한 산업"])),
        regions=", ".join(trend["market"].get("regions", ["글로벌"])),
        rag_insight=rag_insight
    ))

def generate_strategy_top1(top_5_trends, llm):
    """
    ✅ SK AX 전략 제언 (Top 1 테마 중심)
    - 이제 trend는 "테마"이고, 여러 기술×시장 조합을 포함
    """
    
    # Top 1 테마
    top1 = top_5_trends[0]
    theme_name = top1["trend_keyword"]  # "AI Workforce Era"
    
    # 대표 기술/시장
    representative_tech = top1["tech"]
    representative_market = top1["market"]
    
    # 미래 TAM 계산 (대표 시장 기준)
    current_tam = representative_market["tam_usd"]
    cagr = representative_market["cagr"]
    future_tam = int(current_tam * ((1 + cagr) ** 5))
    
    # 🆕 테마에 포함된 모든 기술/시장
    all_tech_names = top1["evidence"]["tech_examples"]
    all_market_names = top1["evidence"]["market_examples"]
    tech_count = top1["evidence"]["tech_count"]
    market_count = top1["evidence"]["market_count"]
    
    # 나머지 테마 요약
    others_summary = "\n".join([
        f"{i}. {t['trend_keyword']} (점수 {t['final_score']:.1f})"
        for i, t in enumerate(top_5_trends[1:], 2)
    ])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 SK 그룹 전략기획 본부장입니다.
        
**중요: 모든 답변은 한글로 작성하세요.**

- 실행 가능한 전략
- 구체적 수치 및 일정
- 리스크 대응 방안
- 최우선 기회 1개에 집중
- 테마는 여러 기술×시장 조합임을 명확히 표현"""),
        
        ("human", """다음 **Top 1 트렌드 테마**를 중심으로 **SK AX 전략 제언**을 작성하세요:

**🎯 최우선 테마:** {theme_name}

**이 테마에 포함된 기술들 ({tech_count}개):**
{all_tech_names}

**이 테마가 타겟하는 시장들 ({market_count}개):**
{all_market_names}

**대표 기술×시장 조합 (분석 기준):**
- 대표 기술: {tech_name} (성숙도 {maturity}점)
- 대표 시장: {market_name} (기회 {opportunity}점)
- 종합 점수: {final_score}점
- 경쟁 강도: {competition}점

**시장 데이터 (대표 시장 기준):**
- TAM: ${tam:,} (2025) → ${future_tam:,} (2030)
- CAGR: {cagr:.1f}%
- 타겟: {target_companies:,}개 기업
- 산업: {industries}
- 지역: {regions}

**나머지 기회:**
{others_summary}

---

다음 구조로 작성:

# PART 3. SK AX 전략 제언

## 3.1 최우선 기회: {theme_name}

### 왜 이 테마인가?

**테마 개요:**

(2-3문단: {theme_name} 테마의 의미와 전략적 중요성)
- 이 테마는 {tech_count}개 기술과 {market_count}개 시장의 융합
- 핵심 기술 조합: {all_tech_names}
- 타겟 시장 조합: {all_market_names}

**시장 기회 규모:**

- **현재 시장 (2025):** ${tam:,}
  - {market_name} 시장 기준
  - 실제로는 {market_count}개 시장의 총합으로 더 큰 기회
  
- **2030년 예상:** ${future_tam:,}
  - CAGR {cagr:.1f}%의 고성장
  
- **타겟 고객:**
  - 규모: {target_companies:,}개 기업 (대표 시장 기준)
  - 주요 산업: {industries}
  - 지역: {regions}

**진입 적기인 이유:**

(3-4문단, 다음 요소 종합 분석)

1. **기술 성숙도:** {maturity}점
   - {tech_name} 등 핵심 기술이 상용화 단계 진입
   - 얼리어답터 고객 확보 가능한 시점
   
2. **시장 성장세:** CAGR {cagr:.1f}%
   - 고성장 시장으로 후발주자도 기회 존재
   
3. **경쟁 강도:** {competition}점
   - 아직 시장 독점 플레이어 부재
   - 중간 수준의 경쟁으로 진입 가능

4. **다층적 기회:**
   - {market_count}개 시장 동시 공략 가능
   - 시장 간 시너지 효과 기대

### 진입 전략

**포지셔닝 전략:**

(차별화 전략 3-4문단)

**1) 빅테크와의 차별화:**
- 빅테크는 대기업 중심, SK AX는 {all_market_names} 중심
- 특화된 기술 조합: {tech_name} + [관련 기술]
- 한국 시장 특화 솔루션

**2) 기술 조합의 우위:**
- 단일 기술이 아닌 **{tech_count}개 기술의 융합**으로 차별화
- 예: {tech_name} + [추가 기술] → 독자적 솔루션
- 핵심 IP 확보 가능 영역 집중

**3) 시장 접근 전략:**
- 1차 타겟: {market_name} (검증 시장)
  - 이유: 가장 높은 기회 점수 ({opportunity}점)
  - 접근: (구체적 방법 2줄)
  
- 2차 타겟: [두 번째 시장] (확장 시장)
  - 이유: (2줄)
  - 접근: (2줄)
  
- 3차 타겟: [세 번째 시장] (장기 시장)
  - 이유: (2줄)
  - 접근: (2줄)

**Go-to-Market 로드맵:**

**Phase 1 (0-6개월): 기술 검증 & POC**
- 핵심 활동:
  - {tech_name} 기반 MVP 개발
  - {market_name} 시장 파일럿 고객 3-5개사 확보
  - 기술 조합 검증 (성공률 70% 이상)
- 목표: 기술적 타당성 확보

**Phase 2 (6-12개월): 시장 진입**
- 핵심 활동:
  - 정식 제품 출시 ({market_name} 중심)
  - 초기 고객 10-15개사 확보
  - 케이스 스터디 3건 이상 확보
- 목표: 초기 매출 발생 (ARR $X million)

**Phase 3 (1-2년): 확장**
- 핵심 활동:
  - 두 번째 시장 진출
  - 고객 50개사 확보
  - 제품 라인업 확장 (기술 조합 다변화)
- 목표: PMF 달성, Break-even

**Phase 4 (2-3년): 스케일업**
- 핵심 활동:
  - 전체 {market_count}개 시장 커버
  - 고객 100개사 이상
  - 해외 진출 시작
- 목표: 시장 리더십 확보

### 예상 성과 및 투자 계획

**3년 목표 (2025-2028):**

- **고객 수:** 100개 기업
  - 1년차: 15개
  - 2년차: 50개
  - 3년차: 100개
  
- **ARR (연간 반복 수익):** $30 million
  - 1년차: $2M
  - 2년차: $10M
  - 3년차: $30M
  
- **시장 점유율:** 5-7%
  - {market_name} 시장 기준
  - 전체 {market_count}개 시장 통합 시 3-5%
  
- **팀 규모:** 80명
  - 기술: 40명 ({tech_count}개 기술 영역)
  - 영업/마케팅: 25명
  - 운영: 15명

**단계별 로드맵:**

| 시기 | Phase | 핵심 활동 | 목표 KPI |
|------|-------|----------|----------|
| 2025 H2 | POC & 검증 | MVP 개발, 파일럿 5개사 | 기술 검증 완료, NPS 70+ |
| 2026 H1 | 시장 진입 | 정식 출시, 초기 고객 15개사 | ARR $2M, CAC < $50K |
| 2026 H2 | 초기 성장 | 케이스 스터디 확보, 고객 30개사 | ARR $5M, Churn < 10% |
| 2027 | PMF 달성 | 두 번째 시장 진출, 고객 50개사 | ARR $10M, Break-even |
| 2028 | 스케일업 | 전체 시장 커버, 고객 100개사 | ARR $30M, 수익성 확보 |

**투자 배분 (3년, 총 $25 million):**

| 항목 | 금액 | 비율 | 설명 |
|------|------|------|------|
| R&D | $10M | 40% | {tech_count}개 기술 개발 및 통합, 핵심 IP 확보 |
| 마케팅 & 영업 | $8M | 32% | {market_count}개 시장 진입 비용, 브랜딩 |
| 인력 채용 | $5M | 20% | 기술 인력 40명, 영업 25명, 운영 15명 |
| 인프라 & 운영 | $2M | 8% | 클라우드, 보안, 법무 등 |

**예상 재무 성과:**

- **1년차 (2025):**
  - 매출: $2M ARR
  - 비용: $8M (R&D $3M + 영업 $3M + 인건비 $2M)
  - 손익: 적자 $6M
  
- **2년차 (2026):**
  - 매출: $10M ARR
  - 비용: $12M
  - 손익: 적자 $2M
  
- **3년차 (2027):**
  - 매출: $30M ARR
  - 비용: $25M
  - 손익: 흑자 $5M
  
- **Break-even:** 2년 9개월차 (2027년 Q3)

## 3.2 중기 기회 (2-5위 테마)

**모니터링 대상:**

{others_summary}

**대응 전략:**

(2-3문단: 2-5위 테마에 대한 접근 방안)

- **즉시:** Top 1 테마 집중, 나머지는 시장 동향 모니터링
- **6개월 후:** Top 1 검증 완료 시, 2-3위 테마 POC 시작
- **1년 후:** Top 1 성공 시, 포트폴리오 확장 (2-3위 본격 진입)
- **2년 후:** 5개 테마 전체 커버 (테마별 전담 팀 구성)

**테마 간 시너지:**
- {theme_name}에서 확보한 기술/고객 기반을 2-5위 테마에 활용
- 예: {tech_name} 기술은 다른 테마에서도 재사용 가능

## 3.3 핵심 리스크 및 대응

### 리스크 1: 빅테크 진입

- **발생 가능성:** 중 (50%)
  - {theme_name} 시장의 성장성이 입증되면 빅테크 관심 증가
  - 특히 {market_name} 시장은 매력적 타겟
  
- **영향도:** 고
  - 가격 경쟁 심화, 고객 확보 난이도 증가
  
- **대응 전략:**
  1. 틈새 시장 선점: 빅테크가 관심 없는 {market_name} 세그먼트 집중
  2. 차별화된 기술 조합: {tech_count}개 기술 융합으로 독자성 확보
  3. 한국 시장 특화: 빅테크가 놓치는 로컬 니즈 공략

### 리스크 2: 기술 발전 속도 차이

- **발생 가능성:** 중 (40%)
  - {tech_name} 등 핵심 기술의 빠른 진화
  - 새로운 기술 등장으로 기존 기술 대체 가능성
  
- **영향도:** 중
  - 기술 투자 방향 수정 필요, R&D 비용 증가
  
- **대응 전략:**
  1. 기술 포트폴리오 다변화: {tech_count}개 기술에 균등 투자
  2. 오픈소스 활용: 커뮤니티 기반 최신 기술 빠른 도입
  3. 파트너십: 선도 기술 기업과 전략적 제휴

### 리스크 3: 규제 변화

- **발생 가능성:** 저 (20%)
  - AI 관련 규제 강화 가능성
  - 특히 {market_name} 시장의 데이터 보호 규제
  
- **영향도:** 고
  - 사업 모델 전면 수정 필요, 출시 지연
  
- **대응 전략:**
  1. 선제적 컴플라이언스: 규제 대응 전담 팀 구성
  2. 정부 협력: 규제 샌드박스 참여, 정책 제안
  3. 유연한 아키텍처: 규제 변화에 빠르게 대응 가능한 설계

### 리스크 4: 시장 수요 검증 실패

- **발생 가능성:** 저-중 (30%)
  - {market_name} 시장의 실제 지불 의사 불확실
  - ROI 검증 실패 시 확산 어려움
  
- **영향도:** 고
  - 사업 전체 중단 가능성
  
- **대응 전략:**
  1. 빠른 POC: 6개월 내 5개사 검증으로 조기 확인
  2. 유연한 피버팅: {market_count}개 시장 중 다른 시장으로 전환
  3. 최소 투자: Phase 1에서 최소 비용으로 검증

---

**중요: 3.4 즉시 실행할 Next Steps는 작성하지 말것**
""")
    ])
    
    response = llm.invoke(prompt.format_messages(
        theme_name=theme_name,
        tech_name=representative_tech["tech_name"],
        market_name=representative_market["demand_name"],
        all_tech_names="\n".join([f"- {t}" for t in all_tech_names]),
        all_market_names="\n".join([f"- {m}" for m in all_market_names]),
        tech_count=tech_count,
        market_count=market_count,
        maturity=representative_tech["maturity_score"],
        opportunity=representative_market["opportunity_score"],
        final_score=top1["final_score"],
        competition=top1["competition"],
        tam=current_tam,
        future_tam=future_tam,
        cagr=cagr * 100,
        target_companies=representative_market.get("target_companies", 0),
        industries=", ".join(representative_market.get("industries", ["다양한 산업"])),
        regions=", ".join(representative_market.get("regions", ["글로벌"])),
        others_summary=others_summary
    ))
    
    return response.content
    return response.content


    """✅ SK AX 전략 제언 (Top 1만 상세히)"""
    
    # Top 1 트렌드
    top1 = top_5_trends[0]
    
    # 나머지 트렌드 요약
    others_summary = "\n".join([
        f"{i}. {t['trend_keyword']} (점수 {t['final_score']:.1f})"
        for i, t in enumerate(top_5_trends[1:], 2)
    ])
    
    # 미래 TAM 계산
    current_tam = top1["market"]["tam_usd"]
    cagr = top1["market"]["cagr"]
    future_tam = int(current_tam * ((1 + cagr) ** 5))
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 SK 그룹 전략기획 본부장입니다.
        
**중요: 모든 답변은 한글로 작성하세요.**

- 실행 가능한 전략
- 구체적 수치 및 일정
- 리스크 대응 방안
- 최우선 기회 1개에 집중"""),
        
        ("human", """다음 Top 1 트렌드를 중심으로 **SK AX 전략 제언**을 작성하세요:

**Top 1 (최우선):**
- 트렌드: {keyword}
- 핵심 기술: {tech_name}
- 타겟 시장: {market_name}
- TAM: ${tam:,} (2025) → ${future_tam:,} (2030)
- CAGR: {cagr:.1f}%
- 기술 성숙도: {maturity}점
- 경쟁 강도: {competition}점

**나머지 기회:**
{others_summary}

---

다음 구조로 작성:

# PART 3. SK AX 전략 제언

## 3.1 최우선 기회: {keyword}

### 시장 기회

**시장 규모 및 성장:**

- 현재 시장: ${tam:,}
- 2030년 예상: ${future_tam:,}
- 연평균 성장률: {cagr:.1f}%

**타겟 고객:**

- 규모: {target_companies:,}개 기업
- 주요 산업: {industries}
- 지역: {regions}

**진입 적기인 이유:**

(3-4문단, 기술 성숙도/시장 성장/경쟁 환경 종합 분석)

### 진입 전략

**포지셔닝:**

(차별화 전략 3-4문단)

- 빅테크와의 차별점
- 중소기업/틈새시장 공략 방안
- 기술적 우위 확보 전략

**타겟 세그먼트:**

- 1차 타겟: (구체적 고객군, 2줄)
- 2차 타겟: (구체적 고객군, 2줄)

**Go-to-Market 전략:**

- 초기 진입: (6개월, 구체적 방법)
- 확장: (1-2년, 구체적 방법)

### 예상 성과 및 투자 계획

**3년 목표:**

- 고객 수: XX개 기업
- ARR (연간 반복 수익): $XX million
- 시장 점유율: X%
- 팀 규모: XX명

**단계별 로드맵:**

| 시기 | Phase | 핵심 활동 | 목표 KPI |
|------|-------|----------|----------|
| 2025 H2 | POC & 검증 | (구체적 활동) | (구체적 KPI) |
| 2026 | 시장 진입 | (구체적 활동) | (구체적 KPI) |
| 2027 | PMF 달성 | (구체적 활동) | (구체적 KPI) |
| 2028-2030 | 스케일업 | (구체적 활동) | (구체적 KPI) |

**투자 배분 (3년, 총 $XX million):**

| 항목 | 금액 | 비율 | 설명 |
|------|------|------|------|
| R&D | $XXM | XX% | (상세 설명) |
| 마케팅 & 영업 | $XXM | XX% | (상세 설명) |
| 인력 채용 | $XXM | XX% | (상세 설명) |
| 인프라 & 운영 | $XXM | XX% | (상세 설명) |

**예상 재무 성과:**

- 1년차: ARR $XX, 손익 (적자 $XX)
- 2년차: ARR $XX, 손익 (적자 $XX)
- 3년차: ARR $XX, 손익 (흑자 $XX)
- Break-even: X년 X개월 차

## 3.2 중기 기회 (2-5위)

**모니터링 대상:**

{others_summary}

**대응 전략:**

(1-2문단, 2-5위 트렌드 중기 접근 방안)

## 3.3 핵심 리스크 및 대응

### 리스크 1: 빅테크 진입

- **발생 가능성:** 중
- **영향도:** 고
- **대응 전략:** (구체적 3줄)

### 리스크 2: 기술 발전 속도 차이

- **발생 가능성:** 중
- **영향도:** 중
- **대응 전략:** (구체적 3줄)

### 리스크 3: 규제 변화

- **발생 가능성:** 저
- **영향도:** 고
- **대응 전략:** (구체적 3줄)

---

**중요: 3.4 즉시 실행할 Next Steps는 작성하지 말것**

""")
    ])
    
    response = llm.invoke(prompt.format_messages(
        keyword=top1["trend_keyword"],
        tech_name=top1["tech"]["tech_name"],
        market_name=top1["market"]["demand_name"],
        tam=current_tam,
        future_tam=future_tam,
        cagr=cagr * 100,
        maturity=top1["tech"]["maturity_score"],
        competition=top1["competition"],
        target_companies=top1["market"].get("target_companies", 0),
        industries=", ".join(top1["market"].get("industries", ["다양한 산업"])),
        regions=", ".join(top1["market"].get("regions", ["글로벌"])),
        others_summary=others_summary
    ))
    
    return response.content

def generate_references(state):
    """
    References 생성
    - 논문, GitHub, 시장 리포트, 전문 문서 출처 정리
    """
    papers = state.get("papers", [])[:10]
    github_repos = state.get("github_repos", [])[:5]
    market_trends = state.get("market_trends", [])[:5]
    
    # ==========================================
    # 1. 학술 논문
    # ==========================================
    if papers:
        paper_refs = []
        for i, p in enumerate(papers, 1):
            authors = p.get('authors', ['Unknown Author'])
            first_author = authors[0] if authors else 'Unknown'
            title = p.get('title', 'No Title')
            date = p.get('publish_date', 'N/A')
            url = p.get('url', '')
            
            paper_refs.append(f"{i}. {first_author}. \"{title}\". arXiv. {date}. {url}")
        
        paper_refs_text = "\n".join(paper_refs)
    else:
        paper_refs_text = "(수집된 논문 없음)"
    
    # ==========================================
    # 2. GitHub 프로젝트
    # ==========================================
    if github_repos:
        github_refs = []
        for i, g in enumerate(github_repos, 1):
            # 이름 우선순위: name > full_name > "Unknown"
            name = g.get('name', g.get('full_name', 'Unknown Project'))
            
            # URL 우선순위: html_url > url > "No URL"
            url = g.get('html_url', g.get('url', 'No URL'))
            
            # Stars 정보 (있으면)
            stars = g.get('stars', g.get('stargazers_count', ''))
            stars_text = f" ({stars:,} stars)" if stars else ""
            
            github_refs.append(f"{i}. {name}{stars_text}: {url}")
        
        github_refs_text = "\n".join(github_refs)
    else:
        github_refs_text = "(수집된 GitHub 프로젝트 없음)"
    
    # ==========================================
    # 3. 시장 리포트 (선택)
    # ==========================================
    if market_trends:
        market_refs = []
        for i, m in enumerate(market_trends, 1):
            demand_name = m.get('demand_name', 'Unknown Market')
            reports = m.get('evidence', {}).get('reports', [])
            
            if reports:
                # 각 시장의 대표 리포트 1개
                report = reports[0]
                title = report.get('title', 'No Title')
                url = report.get('url', '')
                source = report.get('source', 'Unknown Source')
                
                market_refs.append(f"{i}. [{demand_name}] {title} - {source}: {url}")
        
        market_refs_text = "\n".join(market_refs) if market_refs else "(Tavily API를 통해 수집한 최신 시장 리포트)"
    else:
        market_refs_text = "(Tavily API를 통해 수집한 최신 시장 리포트)"
    
    # ==========================================
    # 4. 최종 조합
    # ==========================================
    return f"""# REFERENCES

## 학술 논문

{paper_refs_text}

## GitHub 프로젝트

{github_refs_text}

## 시장 리포트

{market_refs_text}

## 전문 문서

1. OECD AI Principles and Policy Observatory
2. IMF World Economic Outlook Reports
"""
    """References 생성"""
    
    papers = state.get("papers", [])[:10]
    github_repos = state.get("github_repos", [])[:5]
    
    paper_refs = "\n".join([
        f"{i}. {p['authors'][0]}. \"{p['title']}\". arXiv. {p['publish_date']}. {p['url']}"
        for i, p in enumerate(papers, 1)
    ])
    
    github_refs = "\n".join([
        f"{i}. {g['full_name']}. {g['html_url']}"
        for i, g in enumerate(github_repos, 1)
    ])
    
    return f"""# REFERENCES

## 학술 논문

{paper_refs}

## GitHub 프로젝트

{github_refs}

## 시장 리포트

(Tavily API를 통해 수집한 최신 시장 리포트)

## 전문 문서

1. OECD PDF
2. IMF PDF
"""


def generate_appendix():
    """Appendix 생성"""
    
    return """# APPENDIX: 평가 방법론

## A. 분석 범위 및 제약

### 1. 분야 제한

- 본 분석은 AI(Artificial Intelligence) 기술로 범위를 한정
- 포함: Generative AI, LLM, Multimodal AI, Edge AI, AI Agents 등
- 제외: 로보틱스, IoT, 블록체인 등 AI 외 기술

### 2. 데이터 소스

- arXiv 논문 (2023-2025): 기술 성숙도 판단
- GitHub 저장소: 오픈소스 활동 및 실제 구현 수준
- Google Trends: 대중 관심도 및 검색량
- Tavily API: 실시간 시장 리포트 및 뉴스
- 전문 문서 (RAG): 심층 인사이트 (2개 문서, 각 30페이지 제한)

## B. 트렌드 예측 로직

### 1. 기술 성숙도 점수 (0-100점, 가중치 25%)

$$
\\text{기술 성숙도} = 0.5 \\times \\frac{\\text{제품화 비율}}{1.0} + 0.5 \\times \\frac{\\text{GitHub Stars}}{100,000}
$$

- 제품화 비율 = (GitHub 저장소 수) / (논문 수 / 100)
- GitHub Stars = 관련 프로젝트의 총 Star 수

**해석:**

- 90-100점: 상용화 완료 (즉시 사용 가능)
- 70-89점: 얼리어답터 (1-2년 내 대중화)
- 50-69점: 베타 테스트 (2-3년 소요)
- 30-49점: 연구 단계 (5년 이상)
- 0-29점: 초기 연구 (10년 이상)

### 2. 시장 기회 점수 (0-100점, 가중치 35%) ⭐ 가장 중요

$$
\\text{시장 기회} = 0.4 \\times \\min\\left(\\frac{\\text{TAM}}{1B}, 1.0\\right) \\times 100 + 0.3 \\times \\min\\left(\\frac{\\text{타겟 기업 수}}{1M}, 1.0\\right) \\times 100 + 0.3 \\times \\text{정부 지원}
$$

- TAM (Total Addressable Market): 전체 시장 규모 (USD)
- 타겟 기업 수: 잠재 고객 수
- 정부 지원: 있으면 30점, 없으면 0점

### 3. 시장 성장률 점수 (0-100점, 가중치 25%)

$$
\\text{성장률 점수} = \\min\\left(\\frac{\\text{CAGR}}{0.5}, 1.0\\right) \\times 100
$$

- CAGR (Compound Annual Growth Rate): 연평균 성장률
- 50% 이상이면 만점

### 4. 경쟁 강도 (0-100점, 가중치 -15%) ⚠️ 마이너스

$$
\\text{경쟁 강도} = 0.5 \\times \\text{빅테크 관심도} + 0.3 \\times \\min\\left(\\frac{\\text{스타트업 수}}{50}, 1.0\\right) \\times 100 + 0.2 \\times \\text{뉴스 언급도}
$$

**빅테크 관심도:** 수동 평가 (0-100)

- 100: CEO 직접 언급, 주력 사업
- 80: 공식 제품 출시
- 50: 연구 단계
- 20: 관심 없음

## C. 최종 점수 계산

$$
\\text{최종 점수} = 0.25 \\times \\text{기술 성숙도} + 0.35 \\times \\text{시장 기회} + 0.25 \\times \\text{성장률} - 0.15 \\times \\text{경쟁 강도}
$$

**점수 해석:**

- 80-100점: 최우선 투자 영역 (즉시 실행)
- 70-79점: 우선 투자 고려 (6개월 내)
- 60-69점: 중기 투자 검토 (1-2년)
- 50-59점: 모니터링 (2-3년 후 재평가)
- 50점 미만: 제외

## D. Top 5 선정 과정

1. **1단계:** 모든 기술(20개) × 시장(10개) 조합 생성 (200개)
2. **2단계:** 최종 점수 50점 미만 필터링
3. **3단계:** 점수 순 정렬
4. **4단계:** 상위 20개 후보 선정
5. **5단계:** 정성 평가
   - ✅ 스토리 명확성
   - ✅ SK AX 차별화 가능성
   - ✅ 3년 내 실행 가능성
   - ✅ 사회적 임팩트
6. **6단계:** Top 5 최종 선정

## E. 제약사항 및 가정

### 1. 데이터 제약

- arXiv: 영문 논문만 분석
- GitHub: Python 프로젝트 위주 (100 Stars 이상)
- TAM/CAGR: 공개된 시장 리포트 기반 추정치
- 경쟁 강도: 수동 매핑 (주관적 판단 포함)

### 2. 시간 제약

- 분석 기준일: 2025년 10월 23일
- 예측 기간: 2025-2030 (5년)
- 데이터 수집 기간: 2023-2025

### 3. 가정

- 현재 기술 발전 속도 유지
- 규제 환경 급변하지 않음
- 주요 경제 위기 없음

## F. 한계 및 향후 개선 방향

### 1. 현재 한계

- 비영어권 데이터 부족
- 비공개 기업 데이터 미포함
- 단기(1년 미만) 트렌드 변동 반영 제한

### 2. 향후 개선

- 실시간 데이터 업데이트 (주간/월간)
- 다국어 논문 분석 추가
- 기업 IR, 특허 데이터 통합
- 소셜미디어 센티먼트 분석 추가
"""


def convert_md_to_pdf_direct(markdown_content: str, pdf_filename: str):
    """✅ Markdown을 파일로 저장하지 않고 바로 PDF로 변환"""
    try:
        import markdown
        from weasyprint import HTML
        
        # Markdown → HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        
        # HTML 템플릿
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            line-height: 1.8;
            margin: 40px;
            font-size: 11pt;
        }}
        
        
        h1 {{
           color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 24pt;
            page-break-before: always;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 18pt;
        }}

        h3 {{
            color: #666;
            margin-top: 20px;
            font-size: 12pt;
        }}
        
        h4 {{
            color: #666;
            margin-top: 20px;
            font-size: 12pt;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;  /* 표가 페이지 중간에서 안 짤림 */
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
        }}
        
        ul, ol {{
            margin-left: 20px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        strong {{
            color: #2c3e50;
        }}
        
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        @page {{
            size: A4;
            margin: 25mm;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
        
        # ✅ PDF 생성 (stderr 숨기기)
        import sys
        import io
        
        # stderr를 임시로 무시
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        
        try:
            HTML(string=html_template).write_pdf(pdf_filename)
        finally:
            # stderr 복원
            sys.stderr = old_stderr
        
    except ImportError as e:
        raise Exception(f"PDF 변환 라이브러리 없음: {e}\n설치: pip install markdown weasyprint")
    except Exception as e:
        raise Exception(f"PDF 변환 실패: {e}")