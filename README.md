# 코브랜드 주간 트래픽 현황 대시보드

주간 트래픽 보고서 생성을 자동화하는 웹 기반 대시보드 도구입니다.

## 주요 기능

- 📊 엑셀 파일 업로드 및 자동 파싱
- 🤖 AI 기반 트래픽 분석 요약 생성 (AWS Bedrock Claude Sonnet 4.6)
- 📈 인터랙티브 차트 및 테이블 시각화
- 📄 독립형 HTML 보고서 내보내기
- 💾 JSON/HTML 파일 자동 저장 (data 폴더)
- 📊 TOP 20 도메인 UV 분석
- 📱 반응형 디자인

## 빠른 시작

### 자동 실행 (권장)

```bash
# 백엔드 + 프론트엔드 동시 실행
start.bat

# 종료
stop.bat
```

브라우저가 자동으로 열리며 `http://localhost:5173`에서 대시보드를 사용할 수 있습니다.

## 설치 방법

### 1. Python 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
.\venv\Scripts\activate

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 설정을 추가하세요:

```bash
# .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env
```

`.env` 파일에서 다음 항목들을 설정할 수 있습니다:

- **AWS_REGION**: AWS Bedrock 리전 (기본값: us-west-2)
- **MODEL_ID**: 사용할 AI 모델 ID
- **AI_PROMPT_TEMPLATE**: AI 분석에 사용할 프롬프트 템플릿
- **ANTHROPIC_VERSION**: Anthropic API 버전
- **MAX_TOKENS**: AI 응답 최대 토큰 수

### 3. React 대시보드 설정

```bash
cd dashboard
npm install
```

## 수동 실행

### 백엔드 서버 실행

```bash
# 프로젝트 루트에서
python server.py
```

서버는 `http://localhost:8001`에서 실행됩니다.

### 프론트엔드 개발 서버 실행

```bash
cd dashboard
npm run dev
```

프론트엔드는 `http://localhost:5173`에서 실행됩니다.

## 프로젝트 구조

```
cob_weekly/
├── .env                    # 환경 변수 설정 (git에 포함되지 않음)
├── .env.example            # 환경 변수 예시 템플릿
├── requirements.txt        # Python 패키지 목록
├── server.py              # FastAPI 백엔드 서버
├── start.bat              # 자동 시작 스크립트
├── stop.bat               # 자동 종료 스크립트
├── dashboard/             # React 프론트엔드 (Vite)
│   ├── src/
│   │   ├── components/   # React 컴포넌트
│   │   ├── utils/        # 유틸리티 함수
│   │   └── App.jsx       # 메인 앱
│   └── package.json
├── data/                  # 생성된 파일 저장
│   ├── json/             # JSON 파일
│   └── html/             # HTML 보고서
└── docs/                  # 프로젝트 문서
    ├── PRD.md
    └── package_installation.md
```

## 사용 방법

1. **엑셀 파일 준비**

   - 코브랜드 주간 현황 엑셀 파일 준비
   - TOP 20 데이터가 행 128-133에 포함되어야 함

2. **대시보드 접속**

   - `start.bat` 실행
   - 브라우저에서 자동으로 열림

3. **데이터 업로드**

   - 연도, 월, 주차 선택
   - 엑셀 파일 업로드
   - 진행률 바를 통해 분석 진행 상황 확인

4. **결과 확인**

   - AI 요약 확인
   - 차트 및 테이블 확인
   - TOP 20 도메인 분석 확인

5. **내보내기**
   - **JSON 저장**: `data/json/` 폴더에 저장
   - **HTML 내보내기**: `data/html/` 폴더에 저장 + 브라우저 다운로드

## 주요 기능 상세

### TOP 20 데이터 추출

- **텍스트 영역 파싱**: 행 128-133에서 자동 추출
  - 대리점명(행 128), 채널유형(행 129), UV(행 130), 증감률(행 133)
  - D열부터 최대 20개 열 스캔
- **신규 진입 로직**: 증감률 절대값이 0.05% 미만인 경우 "신규진입"으로 표시

### 카테고리별 상세 실적

- **데이터 추출**: 행 15-51 (Index 14-50)
- **기능**: 테이블 숨기기/전체보기 토글 버튼 지원
- **헤더 감지**: 동적 컬럼 인덱스 감지 (UV, 전주UV, 증감률)

### TOP 10 분석

- 브랜드몰 TOP 10
- 제휴사 TOP 10
- 공식인증예약센터 TOP 10
- **UI 개선**: "채널 유형별 TOP 10" 통합 헤더 적용
- 전주대비 증감률 자동 계산

### AI 요약

- AWS Bedrock Claude Sonnet 4.6 사용 (`MODEL_ID=anthropic.claude-sonnet-4-6`)
- 주간 트래픽 핵심 인사이트 생성
- 커스터마이징 가능한 프롬프트

## 환경 변수 커스터마이징

### AI 프롬프트 수정

`.env` 파일에서 `AI_PROMPT_TEMPLATE` 값을 수정하여 AI 분석 프롬프트를 커스터마이징할 수 있습니다.

프롬프트에서 사용 가능한 플레이스홀더:

- `{main_data}`: 메인 데이터
- `{top10_data}`: Top 10 리스트 데이터

## AWS 자격 증명

AWS Bedrock을 사용하려면 AWS 자격 증명이 필요합니다. 다음 방법 중 하나를 사용하세요:

1. AWS CLI 설정: `aws configure`
2. 환경 변수: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
3. IAM 역할 (EC2 등에서 실행 시)

## 기술 스택

### 백엔드

- Python 3.11+
- FastAPI
- pandas, openpyxl
- AWS Bedrock (Claude Sonnet 4.6)

### 프론트엔드

- React 18
- Vite
- Recharts (차트)
- Tailwind CSS
- Lucide React (아이콘)

## 트러블슈팅

### 포트 충돌

- 백엔드: 8001 포트 사용 중인지 확인
- 프론트엔드: 5173 또는 5174 포트 사용

### AWS Bedrock 오류

- AWS 자격 증명 확인
- 리전 설정 확인 (us-west-2 권장)
- 모델 접근 권한 확인

### 엑셀 파일 오류

- 파일 형식 확인 (.xlsx)
- TOP 20 데이터 위치 확인 (행 128-133)
- 인코딩 확인 (UTF-8)

## 라이선스

내부 프로젝트

## 🤖 AI 협업 규칙 및 오류 관리

이 프로젝트는 AI와의 효율적이고 안전한 협업을 위해 다음 문서를 기준으로 작업합니다.
모든 작업 전 아래 문서를 반드시 확인해 주세요.

- **[작업 헌법]** `.ai/instructions.md`: AI 작업의 절대 규칙 (실행 제한, 최소 diff 등)
- **[실행 정책]** `rules/EXEC_POLICY.md`: 명령어 실행 권한 및 절차
- **[변경 이력]** `rules/CHANGELOG.md`: 주요 변경 사항 및 리팩토링 기록
- **[오류 기록]** `logs/ERROR_HISTORY.md`: 발생한 오류와 해결 방법, 재발 방지책
