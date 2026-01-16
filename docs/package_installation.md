# 패키지 설치 및 환경 설정 가이드

본 문서는 '코브랜드 주간 현황 대시보드' 프로젝트를 위한 개발 환경 설정 및 패키지 설치 방법을 안내합니다.

## 1. 사전 요구 사항 (Prerequisites)

- **Node.js**: 최신 LTS 버전 권장 (v18 이상)
- **Python**: 3.8 이상
- **Git**: 소스 코드 관리

## 2. 프로젝트 구조

```
cob_weekly/
├── dashboard/          # React 프론트엔드 프로젝트
├── docs/               # 문서 폴더
├── venv/               # Python 가상 환경
└── ...
```

## 3. 백엔드/AI 환경 설정 (Python)

AWS Bedrock을 활용한 AI 요약 기능을 위해 Python 환경을 구성합니다.

### 3.1 가상 환경 생성 및 활성화

프로젝트 루트 디렉토리(`cob_weekly`)에서 실행합니다.

**Windows:**

```powershell
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
.\venv\Scripts\Activate
```

**Mac/Linux:**

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate
```

### 3.2 필수 패키지 설치

프로젝트에 필요한 모든 Python 패키지를 한 번에 설치합니다.

```bash
pip install -r requirements.txt
```

**설치되는 패키지 목록:**

- `boto3`: AWS SDK for Python (Bedrock API 호출)
- `pandas`: 데이터 분석 및 엑셀 파일 처리
- `fastapi`: 백엔드 API 서버 프레임워크
- `uvicorn`: FastAPI 서버 실행
- `python-dotenv`: 환경 변수 관리 (.env 파일 지원)
- `openpyxl`: 엑셀 파일 읽기/쓰기 엔진
- `python-multipart`: FastAPI 파일 업로드 처리 (Form data 지원)

### 3.3 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하여 AWS 및 AI 설정을 관리합니다.

**`.env` 파일 예시:**

```bash
# AWS Bedrock Configuration
AWS_BEDROCK_REGION=us-west-2
AWS_BEDROCK_MODEL_ID=********
ANTHROPIC_VERSION=********
MAX_TOKENS=****

# Optional: Custom AI Prompt Template
AI_PROMPT_TEMPLATE=
```

**주의사항:**

- `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다.
- AWS 자격 증명은 AWS CLI 또는 환경 변수로 별도 설정이 필요합니다.

## 4. 프론트엔드 환경 설정 (React)

대시보드 UI 및 엑셀 파일 처리를 위한 React 환경을 구성합니다.

### 4.1 React 프로젝트 생성 (Vite)

`dashboard` 폴더에 Vite를 사용하여 React 프로젝트가 생성되었습니다.

```bash
# (참고) 프로젝트 생성 명령어
npx -y create-vite@latest dashboard --template react
```

### 4.2 의존성 패키지 설치

`dashboard` 디렉토리로 이동하여 필요한 패키지를 설치합니다.

```bash
cd dashboard
npm install
```

### 4.3 추가 라이브러리 설치

엑셀 파일 파싱을 위해 `xlsx` (SheetJS) 라이브러리를 설치합니다.

```bash
npm install xlsx
```

## 5. 실행 방법

### 5.1 React 개발 서버 실행

```bash
cd dashboard
npm run dev
```

브라우저에서 `http://localhost:5173` (포트는 변경될 수 있음)으로 접속하여 확인합니다.
