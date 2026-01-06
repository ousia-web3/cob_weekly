# 작업 목록: 코브랜드 주간 트래픽 현황 대시보드

## 1단계: 기획 및 설정

- [x] 요구사항 분석 (`docs/코브랜드주간현황작업.md`)
- [x] PRD 작성 (`docs/PRD.md`)
- [x] 프로젝트 구조 초기화 (React Vite, Python venv)
- [x] 패키지 설치 및 문서화 (`docs/package_installation.md`)
- [x] 데이터용 JSON 스키마 정의

## 2단계: 핵심 구현

- [x] 대시보드 생성 페이지 레이아웃 구현 (Main Container)
- [x] 타이틀 입력 UI 구현 (연도/월/주차 드롭다운)
- [x] 타이틀 자동 생성 로직 구현
- [x] 파일 업로드 구현 (드래그 앤 드롭, .xlsx 지원)
- [x] 엑셀 파싱 로직 구현 (Python openpyxl, 지정된 행/열 범위 처리)
  - [x] Rows 15-51 (카테고리별 상세) 파싱
  - [x] Rows 84-93 (TOP 10) 파싱
  - [x] Rows 103 (디바이스) 파싱
  - [x] Rows 119-124 (주간 추이) 파싱
  - [x] Rows 128-133 (TOP 20 텍스트) 파싱
- [x] 데이터 변환 구현 (Raw -> Dashboard JSON)
- [x] **[Python]** AI 요약 생성 및 통합 (`server.py`)
  - [x] AWS Bedrock (Claude 3.5 Sonnet) 연동
  - [x] 프롬프트 구성 및 호출
  - [x] API 엔드포인트 구현 (`/analyze`)

## 3단계: UI 및 대시보드

- [x] `COB_Weekly UV Dashboard_20251201.html`을 React 컴포넌트로 포팅 (아직 안 된 경우)
- [x] 파싱된 데이터를 대시보드 상태(State)에 연결
- [x] "대시보드 생성" (HTML 내보내기) 기능 구현
- [x] "JSON 저장" 기능 구현

## 4단계: 검증 및 마무리

- [x] 샘플 엑셀 데이터로 테스트
- [x] AI 요약 품질 검증
- [x] HTML 내보내기 렌더링 검증
- [x] 최종 검토

## 5단계: 이메일 기능 및 UI 개선 (2026.01)

- [x] 이메일 발송 기능 구현 (SMTP)
- [x] 이메일 템플릿 최적화 (HTML Table)
- [x] 메일 본문 작성 기능 추가
- [x] 수신자 관리 기능 추가
- [x] 이메일 재발송 및 이력 관리 기능
- [x] UI/UX 개선 (버튼 순서, 안내 문구 등)
