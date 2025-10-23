# config/keywords.py

"""
B2B 중심 '키워드 우주(Seed Universe)' 정의 + 정규화 도우미
- 왜 이 키워드로 수집/평가했는지 설정 레벨에서 명시
- 다음 단계에서 collector_node에서 정규화/화이트리스트 필터로 사용
"""

# ===============================
# 1) B2B 중심 Seed 키워드  [NEW]
# ===============================
# 기술(Tech) 키워드: "제품화 가능성" & "엔터프라이즈 적용성" 중심
SEED_TECH_KEYWORDS_B2B = [
    "LLM agent",                 # 에이전트/업무자동화
    "retrieval augmented generation",  # RAG
    "multimodal speech asr",     # 음성/인식
    "real-time translation",     # 실시간 번역
    "code intelligence",         # 개발자 생산성
    "private LLM",               # 온프레미스/소버린 AI
    "AI observability",          # AI 모니터링/거버넌스
    "MLOps",                     # 운영/관리
    "vector database",           # 인프라
    "enterprise search",         # 사내검색/지식관리
    "document automation",       # 문서 자동화
    "AI contact center",         # 고객센터 자동화
]

# 시장(도메인) 테마: B2B 수요가 뚜렷한 영역
SEED_MARKET_THEMES_B2B = [
    "SME automation",
    "contact center automation",
    "developer productivity",
    "manufacturing quality",
    "privacy and sovereign AI",
    "health diagnostics",
    "personalized learning",
    "marketing content automation",
]


# ==========================================
# 2) 키워드 동의어/표기 정규화 룰  [NEW]
# ==========================================
# 왼쪽 키: 원문(다양한 표기), 오른쪽 값: 캐논컬(정규화 키)
ALIAS_MERGE_RULES = {
    # 생성형/LLM 계열
    "generative ai": "LLM agent",
    "gen ai": "LLM agent",
    "large language model": "LLM agent",
    "llm": "LLM agent",
    "ai agent": "LLM agent",
    "autonomous agent": "LLM agent",

    # RAG
    "retrieval-augmented generation": "retrieval augmented generation",
    "rag": "retrieval augmented generation",

    # 다중모달/ASR/번역
    "speech recognition": "multimodal speech asr",
    "asr": "multimodal speech asr",
    "speech-to-text": "multimodal speech asr",
    "real time translation": "real-time translation",
    "multilingual ai": "real-time translation",

    # 개발자 생산성
    "code generation": "code intelligence",
    "pair programming ai": "code intelligence",

    # 온프레/프라이버시
    "on-prem llm": "private LLM",
    "sovereign ai": "private LLM",
    "privacy ai": "private LLM",

    # 거버넌스/모니터링
    "ai governance": "AI observability",
    "ai monitoring": "AI observability",
    "model monitoring": "AI observability",

    # 문서/검색
    "enterprise rag": "enterprise search",
    "knowledge management": "enterprise search",
    "document processing": "document automation",
}

# B2C·모호·광의 개념 차단
STOPWORDS = {
    "chatbot", "gaming", "filter", "meme", "social", "entertainment",
    "art", "photo", "music cover", "face swap", "deepfake"
}


# ==========================================
# 3) 클러스터 매핑(상위 테마)  [NEW]
# ==========================================
# 기술×시장 조합을 "이야기 있는 5대 테마"로 묶기 위한 룰
# (교차분석 단계에서 generate_trend_keyword() 확장 시 사용)
CLUSTER_RULES = {
    "AI Workforce Era": {
        "tech": ["LLM agent", "document automation", "enterprise search", "code intelligence"],
        "market": ["SME automation", "developer productivity", "contact center automation"]
    },
    "Zero Language Barrier": {
        "tech": ["multimodal speech asr", "real-time translation"],
        "market": ["contact center automation", "SME automation"]
    },
    "1-Person Creator Revolution": {
        "tech": ["LLM agent", "retrieval augmented generation"],
        "market": ["marketing content automation"]
    },
    "Hyper-Personalized Education": {
        "tech": ["LLM agent", "retrieval augmented generation"],
        "market": ["personalized learning"]
    },
    "Invisible AI Infrastructure": {
        "tech": ["private LLM", "AI observability", "MLOps", "vector database"],
        "market": ["privacy and sovereign AI", "developer productivity"]
    }
}


# ==========================================
# 4) 경쟁 강도/트렌드 키워드 (기존 유지) [MOVED/KEPT]
# ==========================================
# 기존 파일의 맵을 유지하되, 필요시 확장
COMPETITION_MAP = {
    "generative AI": 85,
    "large language model": 90,
    "LLM": 90,
    "agent": 50,
    "multimodal": 80,
    "edge AI": 40,
    "automation": 60,
    "text to image": 75
}

# (교차분석에서 여전히 백업 규칙으로 활용 가능)
TREND_KEYWORD_MAP = {
    ("agent", "중소기업"): "AI 직원 시대",
    ("agent", "automation"): "AI 직원 시대",
    ("multimodal", "communication"): "언어 장벽 제로",
    ("multimodal", "language"): "언어 장벽 제로",
    ("text to image", "creator"): "1인 창작자 혁명"
}


# ==========================================
# 5) 기본 검색 키워드 (시드로 사용) [CHANGED]
# ==========================================
# 기존 SEARCH_KEYWORDS를 B2B Seed로 교체 (하위 호환을 위해 이름 유지)
SEARCH_KEYWORDS = SEED_TECH_KEYWORDS_B2B[:]  # [CHANGED]


# ==========================================
# 6) 정규화/필터 도우미  [NEW]
# ==========================================
def canonicalize_keywords(raw_keywords):
    """
    수집 직후 '표준화 + 화이트리스트 + Stopwords 제거'를 수행.
    - ALIAS_MERGE_RULES로 표기 통합
    - STOPWORDS에 해당하는 키워드 제외
    - 화이트리스트(SEED_TECH_KEYWORDS_B2B)에 포함되는 것만 유지
    반환: 정규화된 리스트(중복 제거, 원소는 캐논컬 문자열)
    """
    if not raw_keywords:
        return []

    canon = []
    whitelist = set(k.lower() for k in SEED_TECH_KEYWORDS_B2B)

    for kw in raw_keywords:
        if not kw:
            continue
        k = kw.strip().lower()

        # Stopword 제거
        if any(sw in k for sw in STOPWORDS):
            continue

        # 동의어/표기 정규화
        k = ALIAS_MERGE_RULES.get(k, k)

        # 화이트리스트 필터
        if k.lower() in whitelist:
            canon.append(k)

    # 중복 제거 + 원형 보존(캐논컬만 존재)
    return sorted(list(set(canon)))
