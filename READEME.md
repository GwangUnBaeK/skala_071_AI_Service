# AI Trends 2030 분석

LangGraph를 활용한 2025-2030 AI 트렌드 예측 시스템

## 설치
```bash
# Poetry 설치
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install

# 환경 활성화
poetry shell
```

## 설정

`.env` 파일에 API Key 입력:
```
OPENAI_API_KEY=your-key-here
```

## 실행
```bash
# 환경 테스트
python scripts/test_setup.py

# 전체 분석 실행
python main.py
```

## 구조

- `config/`: 설정 파일
- `state/`: LangGraph State 정의
- `tools/`: 데이터 수집 도구
- `nodes/`: Agent 노드
- `graph/`: Workflow 정의
- `outputs/`: 생성된 보고서