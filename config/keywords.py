# config/keywords.py

# 검색 키워드
SEARCH_KEYWORDS = [
    "generative AI",
    "large language model",
    "LLM agent",
    "multimodal AI",
    "edge AI",
    "AI automation",
    "text to image",
    "AI assistant"
]

# 경쟁 강도 매핑 (수동 정의)
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

# 트렌드 키워드 매핑 (기술 + 시장 → 트렌드 키워드)
TREND_KEYWORD_MAP = {
    ("agent", "중소기업"): "AI 직원 시대",
    ("agent", "automation"): "AI 직원 시대",
    ("multimodal", "communication"): "언어 장벽 제로",
    ("multimodal", "language"): "언어 장벽 제로",
    ("text to image", "creator"): "1인 창작자 혁명",
    ("generative AI", "content"): "1인 창작자 혁명",
    ("edge AI", "device"): "보이지 않는 AI",
    ("edge AI", "privacy"): "보이지 않는 AI",
}