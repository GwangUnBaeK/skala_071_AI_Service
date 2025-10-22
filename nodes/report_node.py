# nodes/report_node.py
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.graph_state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.logger import logger
from config.settings import settings
import markdown2
from weasyprint import HTML
from io import BytesIO
import warnings
warnings.filterwarnings("ignore", message=".*instantiateVariableFont.*", category=UserWarning)

def generate_trend_detail(trend: dict, llm: ChatOpenAI) -> str:
    """각 트렌드 상세 내용 생성 (5-6페이지 분량)"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 20년 경력의 기술 트렌드 분석 전문가입니다. 
McKinsey, Gartner 스타일의 전문적이고 데이터 기반 보고서를 작성합니다.
구체적인 수치, 실제 기업 사례, 시장 데이터를 반드시 포함합니다."""),
        ("human", """
다음 AI 트렌드에 대해 **5-6페이지 분량**의 상세 분석을 작성하세요:

**트렌드 제목:** {keyword}
**핵심 기술:** {tech_name} (기술 성숙도 {maturity}점/100)
**타겟 시장:** {market_name} (시장 기회 점수 {opportunity}점/100)
**시장 규모:** TAM ${tam:,} USD
**연평균 성장률:** {cagr:.1f}%
**경쟁 강도:** {competition}점/100
**주요 GitHub 프로젝트:** {github_projects}

**전문 문서 인사이트:**
{rag_insight}

---

다음 구조로 **5-6페이지 분량**을 작성하세요:

### {rank}. {keyword}

#### 1. 개요 및 핵심 메시지 (1페이지)
- 이 트렌드를 한 문장으로 요약
- 2030년 예상 모습 (구체적 시나리오)
- 핵심 데이터 포인트 3가지
  * 기술 성숙도: {maturity}점 → 의미 해석
  * 시장 규모: ${tam:,} → 비교 대상 제시
  * 성장률: {cagr:.1f}% CAGR → 업계 평균과 비교

#### 2. 기술 배경 및 발전 단계 (1.5페이지)
**2.1 기술 설명**
- {tech_name} 기술의 핵심 원리
- 기존 기술 대비 혁신성

**2.2 기술 성숙도 분석**
- 현재 단계: 연구/베타/얼리어답터/상용화 중 어디?
- 근거: 논문 수({paper_count}편), GitHub Stars({github_stars:,}개)
- 주요 오픈소스 프로젝트: {github_projects}
- 대표 기업 및 제품 (최소 3개 실제 사례)

**2.3 기술 로드맵**
- 2025: 현재 수준
- 2027: 중기 전망
- 2030: 장기 전망

#### 3. 시장 기회 분석 (1.5페이지)
**3.1 시장 수요**
- 문제 정의: {market_problem}
- 왜 지금인가? (타이밍)
- 타겟 고객: {target_companies:,}개 기업

**3.2 시장 규모 및 성장**
- TAM: ${tam:,} (2025년 기준)
- 2030년 예상: ${future_tam:,.0f}
- 주요 산업: {industries}
- 지역별 분포: {regions}

**3.3 실제 적용 사례**
(각 사례당 3-4문장으로 구체적 설명)
- 사례 1: [기업명] - 도입 배경, 효과, ROI
- 사례 2: [기업명] - 도입 배경, 효과, ROI
- 사례 3: [기업명] - 도입 배경, 효과, ROI

#### 4. 경쟁 환경 분석 (1페이지)
**4.1 주요 경쟁자**
- 빅테크: Google, Microsoft, OpenAI 등의 움직임
- 스타트업: 주목할 만한 스타트업 3곳
- 경쟁 강도: {competition}점 → 해석

**4.2 진입 장벽**
- 기술적 장벽
- 자본 요구사항
- 규제 이슈

#### 5. SK AX 전략 제언 (1페이지)
**5.1 진입 전략**
- 타이밍: 즉시/1년 후/2년 후?
- 포지셔닝: 어떤 차별화?
- 타겟: B2B/B2C? 어떤 세그먼트?

**5.2 실행 로드맵**
- Phase 1 (6개월): POC, 목표 및 KPI
- Phase 2 (1년): 시장 진입, 목표 및 KPI
- Phase 3 (3년): 스케일업, 목표 및 KPI

**5.3 투자 및 수익 전망**
- 필요 투자액: $XX million
- 3년 후 예상 ARR: $XX million
- Break-even 시점: X년 후

**5.4 리스크 및 대응**
- 리스크 1: [설명] → 대응책
- 리스크 2: [설명] → 대응책
- 리스크 3: [설명] → 대응책

---

**중요:**
- 모든 수치는 구체적으로 (예: "많은" → "500만 개")
- 모든 사례는 실명으로 (예: "한 기업" → "삼성전자")
- 추상적 표현 금지, 데이터 기반 서술
- 5-6페이지 분량 준수 (약 3,000-4,000자)
        """)
    ])
    
    # RAG 인사이트 정리
    rag_insight = trend.get("rag_insight", {}).get("answer", "전문 문서 분석 없음")
    
    # GitHub 프로젝트
    github_projects = ", ".join(trend["tech"].get("related_projects", ["없음"])[:3])
    
    response = llm.invoke(prompt.format_messages(
        rank=trend["rank"],
        keyword=trend["trend_keyword"],
        tech_name=trend["tech"]["tech_name"],
        maturity=trend["tech"]["maturity_score"],
        market_name=trend["market"]["demand_name"],
        market_problem=trend["market"].get("problem_statement", "시장 수요 존재"),
        opportunity=trend["market"]["opportunity_score"],
        tam=trend["market"]["tam_usd"],
        cagr=trend["market"]["cagr"] * 100,
        competition=trend["competition"],
        paper_count=trend["tech"].get("paper_count", 0),
        github_stars=trend["tech"].get("github_stars_total", 0),
        github_projects=github_projects,
        target_companies=trend["market"].get("target_companies", 0),
        industries=", ".join(trend["market"].get("industries", ["다양한 산업"])),
        regions=", ".join(trend["market"].get("regions", ["글로벌"])),
        rag_insight=rag_insight
    ))
    
    return response.content

def generate_executive_summary(top_5_trends: list, llm: ChatOpenAI) -> str:
    """Executive Summary 생성"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 경영진을 위한 간결하고 임팩트 있는 요약을 작성하는 전문가입니다."),
        ("human", """
다음 Top 5 AI 트렌드를 바탕으로 1페이지 분량의 Executive Summary를 작성하세요:

{trends_summary}

다음 내용을 포함하세요:
1. 핵심 메시지 (2-3문장)
2. Top 5 트렌드 요약 (각 2줄)
3. SK AX를 위한 핵심 제언 3가지
4. 즉시 실행 가능한 Next Action

임원이 2분 안에 읽을 수 있도록 간결하고 명확하게 작성하세요.
        """)
    ])
    
    trends_summary = "\n\n".join([
        f"**{t['rank']}. {t['trend_keyword']}** (점수: {t['final_score']:.1f})\n"
        f"- 기술: {t['tech']['tech_name']} (성숙도 {t['tech']['maturity_score']:.1f})\n"
        f"- 시장: {t['market']['demand_name']} (TAM ${t['market']['tam_usd']:,}, 성장률 {t['market']['cagr']*100:.0f}%)"
        for t in top_5_trends
    ])
    
    response = llm.invoke(prompt.format_messages(trends_summary=trends_summary))
    return response.content

def collect_references(top_5_trends: list, papers: list, rag_analysis: dict) -> str:
    """참고 문헌 수집"""
    
    references = "## REFERENCES\n\n"
    references += "### 학술 논문\n\n"
    
    # 상위 10개 논문
    for i, paper in enumerate(papers[:10], 1):
        authors = ", ".join(paper.get("authors", ["Unknown"])[:3])
        references += f"{i}. {authors}. \"{paper['title']}\". arXiv. {paper['publish_date']}. {paper['url']}\n\n"
    
    references += "\n### GitHub 프로젝트\n\n"
    
    # 각 트렌드의 주요 프로젝트
    github_set = set()
    for trend in top_5_trends:
        for project in trend["tech"].get("related_projects", [])[:2]:
            github_set.add(project)
    
    for i, project in enumerate(sorted(github_set)[:10], 1):
        references += f"{i}. {project}. https://github.com/{project}\n\n"
    
    references += "\n### 시장 리포트\n\n"
    
    # Tavily 검색 결과
    report_idx = 1
    for trend in top_5_trends:
        tavily_reports = trend["market"].get("tavily_reports", [])
        for report in tavily_reports[:2]:
            references += f"{report_idx}. \"{report['title']}\". {report['source']}. {report['url']}\n\n"
            report_idx += 1
    
    # RAG 문서
    if rag_analysis.get("loaded_documents"):
        references += "\n### 전문 문서\n\n"
        for i, doc in enumerate(rag_analysis["loaded_documents"], 1):
            references += f"{i}. {doc}\n\n"
    
    return references

def generate_appendix() -> str:
    """부록: 평가 로직 설명"""
    
    appendix = """## APPENDIX: 평가 방법론

### A. 분석 범위 및 제약

**1. 분야 제한**
- 본 분석은 **AI(Artificial Intelligence) 기술**로 범위를 한정
- 포함: Generative AI, LLM, Multimodal AI, Edge AI, AI Agents 등
- 제외: 로보틱스, IoT, 블록체인 등 AI 외 기술

**2. 데이터 소스**
- **arXiv 논문** (2023-2025): 기술 성숙도 판단
- **GitHub 저장소**: 오픈소스 활동 및 실제 구현 수준
- **Google Trends**: 대중 관심도 및 검색량
- **Tavily API**: 실시간 시장 리포트 및 뉴스
- **전문 문서 (RAG)**: 심층 인사이트 (2개 문서, 각 30페이지 제한)

---

### B. 트렌드 예측 로직

**1. 기술 성숙도 점수 (0-100점, 가중치 25%)**

$$
\\text{기술 성숙도} = 0.5 \\times \\frac{\\text{제품화 비율}}{1.0} + 0.5 \\times \\frac{\\text{GitHub Stars}}{100,000}
$$

- **제품화 비율** = (GitHub 저장소 수) / (논문 수 / 100)
- **GitHub Stars** = 관련 프로젝트의 총 Star 수
- **해석:**
  - 90-100점: 상용화 완료 (즉시 사용 가능)
  - 70-89점: 얼리어답터 (1-2년 내 대중화)
  - 50-69점: 베타 테스트 (2-3년 소요)
  - 30-49점: 연구 단계 (5년 이상)
  - 0-29점: 초기 연구 (10년 이상)

**2. 시장 기회 점수 (0-100점, 가중치 35%)** ⭐ 가장 중요

$$
\\text{시장 기회} = 0.4 \\times \\min\\left(\\frac{\\text{TAM}}{1B}, 1.0\\right) \\times 100 + 0.3 \\times \\min\\left(\\frac{\\text{타겟 기업 수}}{1M}, 1.0\\right) \\times 100 + 0.3 \\times \\text{정부 지원}
$$

- **TAM (Total Addressable Market)**: 전체 시장 규모 (USD)
- **타겟 기업 수**: 잠재 고객 수
- **정부 지원**: 있으면 30점, 없으면 0점

**3. 시장 성장률 점수 (0-100점, 가중치 25%)**

$$
\\text{성장률 점수} = \\min\\left(\\frac{\\text{CAGR}}{0.5}, 1.0\\right) \\times 100
$$

- **CAGR (Compound Annual Growth Rate)**: 연평균 성장률
- 50% 이상이면 만점

**4. 경쟁 강도 (0-100점, 가중치 -15%)** ⚠️ 마이너스

$$
\\text{경쟁 강도} = 0.5 \\times \\text{빅테크 관심도} + 0.3 \\times \\min\\left(\\frac{\\text{스타트업 수}}{50}, 1.0\\right) \\times 100 + 0.2 \\times \\text{뉴스 언급도}
$$

- **빅테크 관심도**: 수동 평가 (0-100)
  - 100: CEO 직접 언급, 주력 사업
  - 80: 공식 제품 출시
  - 50: 연구 단계
  - 20: 관심 없음

---

### C. 최종 점수 계산

$$
\\text{최종 점수} = 0.25 \\times \\text{기술 성숙도} + 0.35 \\times \\text{시장 기회} + 0.25 \\times \\text{성장률} - 0.15 \\times \\text{경쟁 강도}
$$

**점수 해석:**
- **80-100점**: 최우선 투자 영역 (즉시 실행)
- **70-79점**: 우선 투자 고려 (6개월 내)
- **60-69점**: 중기 투자 검토 (1-2년)
- **50-59점**: 모니터링 (2-3년 후 재평가)
- **50점 미만**: 제외

---

### D. Top 5 선정 과정

1. **1단계**: 모든 기술(20개) × 시장(10개) 조합 생성 (200개)
2. **2단계**: 최종 점수 50점 미만 필터링
3. **3단계**: 점수 순 정렬
4. **4단계**: 상위 20개 후보 선정
5. **5단계**: 정성 평가
   - ✅ 스토리 명확성
   - ✅ SK AX 차별화 가능성
   - ✅ 3년 내 실행 가능성
   - ✅ 사회적 임팩트
6. **6단계**: Top 5 최종 선정

---

### E. 제약사항 및 가정

**1. 데이터 제약**
- arXiv: 영문 논문만 분석
- GitHub: Python 프로젝트 위주 (100 Stars 이상)
- TAM/CAGR: 공개된 시장 리포트 기반 추정치
- 경쟁 강도: 수동 매핑 (주관적 판단 포함)

**2. 시간 제약**
- 분석 기준일: {analysis_date}
- 예측 기간: 2025-2030 (5년)
- 데이터 수집 기간: 2023-2025

**3. 가정**
- 현재 기술 발전 속도 유지
- 규제 환경 급변하지 않음
- 주요 경제 위기 없음

---

### F. 한계 및 향후 개선 방향

**1. 현재 한계**
- 비영어권 데이터 부족
- 비공개 기업 데이터 미포함
- 단기(1년 미만) 트렌드 변동 반영 제한

**2. 향후 개선**
- 실시간 데이터 업데이트 (주간/월간)
- 다국어 논문 분석 추가
- 기업 IR, 특허 데이터 통합
- 소셜미디어 센티먼트 분석 추가

"""
    
    analysis_date = datetime.now().strftime("%Y년 %m월 %d일")
    return appendix.replace("{analysis_date}", analysis_date)

def markdown_to_pdf(markdown_text: str, output_path: str):
    """Markdown을 PDF로 변환"""
    
    # CSS 스타일
    css_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
        
        body {
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            margin: 2cm;
        }
        h1 {
            font-size: 24pt;
            font-weight: 700;
            color: #1a1a1a;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        h2 {
            font-size: 18pt;
            font-weight: 700;
            color: #0066cc;
            margin-top: 25px;
            page-break-before: always;
        }
        h3 {
            font-size: 14pt;
            font-weight: 700;
            color: #333;
            margin-top: 20px;
        }
        h4 {
            font-size: 12pt;
            font-weight: 700;
            color: #666;
            margin-top: 15px;
        }
        p {
            margin: 10px 0;
            text-align: justify;
        }
        ul, ol {
            margin: 10px 0 10px 20px;
        }
        li {
            margin: 5px 0;
        }
        strong {
            font-weight: 700;
            color: #0066cc;
        }
        code {
            background: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        blockquote {
            border-left: 4px solid #0066cc;
            padding-left: 15px;
            margin: 15px 0;
            color: #666;
            font-style: italic;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background: #0066cc;
            color: white;
            font-weight: 700;
        }
        hr {
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }
    </style>
    """
    
    # Markdown → HTML
    html_content = markdown2.markdown(
        markdown_text,
        extras=["tables", "fenced-code-blocks", "strike", "task_list"]
    )
    
    # 전체 HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        {css_style}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # PDF 생성
    HTML(string=full_html).write_pdf(output_path)

def report_generation_node(state: GraphState) -> GraphState:
    """
    Agent 5: 최종 보고서 생성 (PDF)
    """
    logger.info("="*70)
    logger.info("📝 Agent 5: 최종 보고서 생성 시작")
    logger.info("="*70)
    
    top_5_trends = state.get("top_5_trends", [])
    rag_analysis = state.get("rag_analysis", {})
    papers = state.get("papers", [])
    
    if not top_5_trends:
        logger.error("❌ Top 5 트렌드가 없습니다!")
        return {
            "final_report": "Error: Top 5 트렌드 없음",
            "current_step": "report_failed"
        }
    
    logger.info(f"\n보고서 생성 시작...")
    logger.info(f"   - Top 5 트렌드: {len(top_5_trends)}개")
    logger.info(f"   - RAG 분석: {'포함' if rag_analysis.get('answer') else '없음'}\n")
    
    # LLM 초기화
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    # ========================================
    # 보고서 구성
    # ========================================
    
    report = f"""# AI TRENDS 2025-2030
## 5년 후 세상을 바꿀 5대 AI 트렌드

**보고서 생성일:** {datetime.now().strftime("%Y년 %m월 %d일")}  
**분석 기간:** 2023년 1월 - 2025년 10월  
**분석 대상:** AI 기술 및 시장

---

"""
    
    # ========================================
    # PART 1: EXECUTIVE SUMMARY
    # ========================================
    
    logger.info("1️⃣ Executive Summary 생성 중...")
    
    report += "## EXECUTIVE SUMMARY\n\n"
    
    try:
        summary = generate_executive_summary(top_5_trends, llm)
        report += summary + "\n\n"
        logger.info("   ✓ 완료\n")
    except Exception as e:
        logger.error(f"   ✗ 실패: {e}\n")
        report += "*Executive Summary 생성 실패*\n\n"
    
    report += "### 🎯 Top 5 트렌드 한눈에 보기\n\n"
    
    for trend in top_5_trends:
        report += f"**{trend['rank']}. {trend['trend_keyword']}** (최종 점수: {trend['final_score']:.1f}/100)\n"
        report += f"- 핵심 기술: {trend['tech']['tech_name']} (성숙도 {trend['tech']['maturity_score']:.1f}/100)\n"
        report += f"- 타겟 시장: {trend['market']['demand_name']} (기회 {trend['market']['opportunity_score']:.1f}/100)\n"
        report += f"- 시장 규모: TAM ${trend['market']['tam_usd']:,} USD\n"
        report += f"- 연성장률: {trend['market']['cagr']*100:.1f}% CAGR\n"
        report += f"- 경쟁 강도: {trend['competition']:.1f}/100\n\n"
    
    report += "\n---\n\n"
    
    # ========================================
    # PART 2: 분석 방법론
    # ========================================
    
    report += "## PART 1. 분석 방법론\n\n"
    report += "### 1.1 데이터 소스\n\n"
    report += f"- **arXiv 논문**: {len(papers)}편 (2023-2025)\n"
    report += f"- **GitHub 저장소**: {len(state.get('github_repos', []))}개 프로젝트\n"
    report += f"- **Google Trends**: {len(state.get('google_trends', {}))}개 키워드\n"
    report += "- **시장 리포트**: Tavily API 실시간 검색\n"
    
    if rag_analysis.get("loaded_documents"):
        report += f"- **전문 문서 (RAG)**: {', '.join(rag_analysis['loaded_documents'])}\n"
    
    report += "\n### 1.2 평가 기준\n\n"
    report += "| 기준 | 가중치 | 설명 |\n"
    report += "|------|--------|------|\n"
    report += "| 기술 성숙도 | 25% | 논문 대비 제품화 비율, GitHub 활동도 |\n"
    report += "| 시장 기회 | 35% | TAM, 타겟 기업 수, 정부 지원 |\n"
    report += "| 시장 성장률 | 25% | CAGR (연평균 성장률) |\n"
    report += "| 경쟁 강도 | -15% | 빅테크 관심도, 스타트업 경쟁 |\n\n"
    
    report += "*자세한 평가 로직은 부록(APPENDIX) 참조*\n\n"
    report += "\n---\n\n"
    
    # ========================================
    # PART 3: 5대 트렌드 상세 분석
    # ========================================
    
    report += "## PART 2. 5대 트렌드 상세 분석\n\n"
    report += "*각 트렌드는 5-6페이지 분량으로 구성되어 있습니다.*\n\n"
    report += "---\n\n"
    
    for i, trend in enumerate(top_5_trends, 1):
        logger.info(f"2️⃣ [{i}/5] '{trend['trend_keyword']}' 상세 내용 생성 중...")
        
        try:
            detail = generate_trend_detail(trend, llm)
            report += detail + "\n\n---\n\n"
            logger.info(f"      ✓ 완료 ({len(detail):,}자)\n")
            
        except Exception as e:
            logger.error(f"      ✗ 실패: {e}\n")
            report += f"### {i}. {trend['trend_keyword']}\n\n"
            report += f"*상세 내용 생성 실패: {str(e)}*\n\n---\n\n"
    
    # ========================================
    # PART 4: SK AX 전략 제언
    # ========================================
    
    logger.info("3️⃣ SK AX 전략 제언 생성 중...")
    
    report += "## PART 3. SK AX 전략 제언\n\n"
    
    report += "### 3.1 우선순위 Top 3 기회\n\n"
    
    for i, trend in enumerate(top_5_trends[:3], 1):
        report += f"#### {i}. {trend['trend_keyword']}\n\n"
        report += f"**시장 기회**\n"
        report += f"- 시장 규모: ${trend['market']['tam_usd']:,} (2025) → ${int(trend['market']['tam_usd'] * (1 + trend['market']['cagr'])**5):,} (2030 예상)\n"
        report += f"- 타겟 고객: {trend['market'].get('target_companies', 0):,}개 기업\n"
        report += f"- 주요 산업: {', '.join(trend['market'].get('industries', ['다양한 산업']))}\n\n"
        
        report += f"**진입 전략**\n"
        report += f"- 포지셔닝: 중소기업/동남아시아 특화\n"
        report += f"- 차별화: {trend['tech']['tech_name']} 기술 기반 맞춤형 솔루션\n"
        report += f"- 타이밍: {'즉시' if trend['tech']['maturity_score'] > 70 else '1년 내'} (기술 성숙도 {trend['tech']['maturity_score']:.0f}점)\n\n"
        
        report += f"**예상 성과**\n"
        report += f"- 3년 후 ARR: ${int(trend['market']['tam_usd'] * 0.001):,} (TAM의 0.1% 점유 가정)\n"
        report += f"- Break-even: 2년 차 예상\n"
        report += f"- 필요 투자: ${int(trend['market']['tam_usd'] * 0.00001):,}\n\n"
    
    report += "### 3.2 통합 실행 로드맵\n\n"
    report += "| 시기 | Phase | 주요 활동 | 목표 |\n"
    report += "|------|-------|----------|------|\n"
    report += "| 2025 H2 | POC | 기술 검증, 파일럿 고객 확보 | 5개 기업 POC 완료 |\n"
    report += "| 2026 | 시장 진입 | 제품 출시, 초기 고객 확보 | 50개 기업, ARR $500K |\n"
    report += "| 2027 | PMF | Product-Market Fit 달성 | 200개 기업, ARR $2M |\n"
    report += "| 2028-2030 | 스케일업 | 지역 확장, 제품 라인업 확대 | 1,000개 기업, ARR $10M |\n\n"
    
    report += "### 3.3 투자 배분 계획\n\n"
    report += "**총 투자 규모 (3년)**: $20 Million\n\n"
    
    report += "| 항목 | 금액 | 비율 |\n"
    report += "|------|------|------|\n"
    report += "| R&D (기술 개발) | $8M | 40% |\n"
    report += "| 마케팅 & 영업 | $6M | 30% |\n"
    report += "| 인력 채용 | $4M | 20% |\n"
    report += "| 인프라 & 기타 | $2M | 10% |\n\n"
    
    report += "### 3.4 핵심 리스크 및 대응 전략\n\n"
    
    risks = [
        {
            "risk": "빅테크 진입",
            "probability": "중",
            "impact": "고",
            "mitigation": "중소기업/틈새시장 집중, 빠른 PMF 달성"
        },
        {
            "risk": "기술 발전 속도 차이",
            "probability": "중",
            "impact": "중",
            "mitigation": "오픈소스 활용, 파트너십 강화"
        },
        {
            "risk": "규제 변화",
            "probability": "저",
            "impact": "고",
            "mitigation": "정부 정책 모니터링, 컴플라이언스 팀 운영"
        }
    ]
    
    for risk in risks:
        report += f"**{risk['risk']}**\n"
        report += f"- 발생 가능성: {risk['probability']} | 영향도: {risk['impact']}\n"
        report += f"- 대응: {risk['mitigation']}\n\n"
    
    report += "\n---\n\n"
    
    # ========================================
    # REFERENCES
    # ========================================
    
    logger.info("4️⃣ References 생성 중...")
    
    references = collect_references(top_5_trends, papers, rag_analysis)
    report += references
    report += "\n---\n\n"
    
    logger.info("   ✓ 완료\n")
    
    # ========================================
    # APPENDIX
    # ========================================
    
    logger.info("5️⃣ Appendix 생성 중...")
    
    appendix = generate_appendix()
    report += appendix
    
    logger.info("   ✓ 완료\n")
    
    # ========================================
    # 보고서 저장 (Markdown + PDF)
    # ========================================
    
    os.makedirs("outputs/reports", exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Markdown 저장
    md_path = f"outputs/reports/AI_TRENDS_{timestamp}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"📄 Markdown 저장: {md_path}")
    
    # 2. PDF 변환
    logger.info("6️⃣ PDF 변환 중...")
    
    pdf_path = f"outputs/reports/AI_TRENDS_{timestamp}.pdf"
    
    try:
        markdown_to_pdf(report, pdf_path)
        logger.info(f"📕 PDF 저장: {pdf_path}")
        logger.info(f"   크기: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB\n")
        
    except Exception as e:
        logger.error(f"   ✗ PDF 변환 실패: {e}\n")
        logger.info("   → Markdown 파일은 정상 저장되었습니다.\n")
        pdf_path = None
    
    # ========================================
    # 완료
    # ========================================
    
    logger.info("="*70)
    logger.info("✅ Agent 5: 보고서 생성 완료")
    logger.info("="*70)
    logger.info(f"   📄 Markdown: {md_path}")
    if pdf_path:
        logger.info(f"   📕 PDF: {pdf_path}")
    logger.info(f"   📊 총 길이: {len(report):,}자")
    logger.info("="*70 + "\n")
    
    return {
        "final_report": report,
        "messages": [{
            "role": "assistant",
            "content": f"보고서 생성 완료 (MD + PDF)"
        }],
        "step_report": "completed"
    }
