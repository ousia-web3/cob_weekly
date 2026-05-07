# 변경 이력 (CHANGELOG)

이 문서는 프로젝트의 주요 수정, 개선, 오류 조치 이력을 기록합니다.
AI는 작업 완료 후 이 문서를 갱신해야 합니다.

## 양식 가이드

- **날짜**: YYYY-MM-DD
- **변경 대상**: 수정된 파일명 또는 모듈
- **유형**: [오류수정], [리팩토링], [기능개선], [문서화]
- **내용**:
  - **문제 요약**: 무엇이 문제였는지 간단히
  - **수정 내용**: 어떻게 고쳤는지
  - **재발 방지**: 향후 주의할 점

---

## 2026-03-04

- **변경 대상**: `dashboard/src/components/DashboardPreview.jsx`, `App.jsx`, `main.jsx`, `ErrorBoundary.jsx` (신규)
- **유형**: [기능개선], [오류수정]
- **내용**:
  - **작업 요약**: AI 요약 수정 버튼 클릭 시 흰 화면 현상 대응 및 수정/추가/삭제 기능 강화
  - **수정 내용**:
    - **AI 요약 수정 모드**: 기생성된 AI 요약 유지, 수정·추가·삭제 지원 (추가 버튼, 삭제 버튼 per 항목)
    - **방어 로직**: `handleEditInsights`에서 title/content를 `String()`으로 강제, input/textarea value에 `String()` 적용, `coBrandTop20`/`categories` null-safe 처리
    - **상태 업데이트**: `requestAnimationFrame`으로 수정 모드 진입 시 렌더 블로킹 완화
    - **Error Boundary**: `ErrorBoundary.jsx` 신규 생성, `main.jsx`/`App.jsx`에 적용하여 크래시 시 에러 메시지 표시
  - **재발 방지**: aiInsight 사용처(exportUtils, generate_email_report)와 `{ title, content }` 구조 호환 유지. 수정 시 이 기준을 훼손하지 말 것.

---

## 2026-01-16

- **변경 대상**: `server.py`
- **유형**: [오류수정]
- **내용**:
  - **문제 요약**: 엑셀 파일 업로드 시 행 개수가 부족한 경우(131행) 증감률 데이터(133행) 접근 시 `IndexError` 발생
  - **수정 내용**: `extract_top20_from_cells` 함수에서 `growth_row` 접근 전 데이터프레임 길이 확인 로직(`if growth_row < len(df):`) 추가
  - **재발 방지**: 고정 인덱스로 데이터 접근 시 반드시 데이터프레임의 크기(shape)를 먼저 검증하도록 함

## 2026-01-19

- **변경 대상**: `docs/` (전체 문서), `manual.html`, `manual_presentation.html`
- **유형**: [문서화], [기능개선]
- **내용**:
  - **작업 요약**: 프로젝트 문서 현행화 및 사용자 매뉴얼 HTML 버전 생성
  - **수정 내용**:
    - `PRD.md`, `기술정책정의서.md`, `프로젝트_완료_보고서.md` 등 주요 문서 최신 기능(이메일 서비스, 에디터 등) 반영 업데이트
    - 불필요한 임시 파일(`task.md` 등) 삭제 및 정리
    - `manual.html`: 상세 사용자 매뉴얼 HTML 생성 (내부 접속 정보, 상세 가이드 포함)
    - `manual_presentation.html`: PPT 스타일의 프레젠테이션용 매뉴얼 생성
    - **기능 추가**: HTML 매뉴얼 내 접속 주소 '복사' 버튼 기능(JavaScript) 구현
  - **비고**: 내부 임직원용 접속 주소(`192.168.82.105`) 및 방화벽 안내 추가됨

## 2026-01-20

- **변경 대상**: `email_service.py`
- **유형**: [기능개선]
- **내용**:
  - **문제 요약**: 메일 수신자가 10명 이상일 때도 수신자 목록에 1명씩만 표기되는 현상 (개별 발송 방식)
  - **수정 내용**: `send_email` 메서드에서 수신자 목록을 순회하며 개별 발송하던 로직을, 수신자 전체를 `To` 헤더에 쉼표로 구분하여 넣고 한 번에 발송(`server.send_message`)하는 방식으로 변경
  - **결과**: 메일 수신 시 전체 수신자 목록이 정상적으로 표기됨

- **변경 대상**: `generate_email_report.py`
- **유형**: [기능개선], [UI/UX]
- **내용**:
  - **문제 요약**: 아웃룩(Outlook) 앱 및 데스크탑 버전에서 이메일 템플릿의 레이아웃(배경색, 정렬, 그라데이션 등)이 깨져 보이는 현상
  - **수정 내용**:
    - 전체 레이아웃을 `div` 기반에서 `table` 기반(Table-based Layout)으로 전면 리팩토링
    - Outlook에서 지원하지 않는 CSS(그라데이션, flexbox 등) 제거 및 대체 (단색 배경, 테이블 정렬)
    - `<!--[if mso]>` 조건부 주석을 추가하여 Outlook 전용 폰트 설정 보강
    - AI 요약(Insights) 및 카테고리 상세 영역의 컨테이너 구조를 테이블로 변경하여 안정성 확보
  - **결과**: Outlook을 포함한 다양한 이메일 클라이언트에서 일관된 디자인 유지

- **변경 대상**: `server.py`, `dashboard/src/App.jsx`, `dashboard/src/components/DashboardPreview.jsx`
- **유형**: [기능개선]
- **내용**:
  - **작업 요약**: 대시보드 내 '핵심 요약 재생성' 버튼 및 기능 구현
  - **수정 내용**:
    - `server.py`: `generate_ai_insights` 함수가 AI 생성 결과뿐만 아니라 프롬프트 컨텍스트(Main Data, Top 10 Data)도 함께 반환하도록 수정. 컨텍스트 데이터를 받아 요약을 다시 생성하는 `/regenerate-summary` API 엔드포인트 추가.
    - `App.jsx`: 대시보드 데이터에 AI 컨텍스트 정보를 저장하고, 재생성 버튼 클릭 시 해당 컨텍스트로 API를 호출하여 요약을 갱신하는 핸들러(`handleRegenerateInsights`) 구현.
    - `DashboardPreview.jsx`: 핵심 요약 섹션의 '수정' 버튼 좌측에 '핵심요약 재생성' 버튼(Refresh 아이콘 포함) 추가.
  - **비고**: 재생성 기능은 파일을 새로 업로드하여 컨텍스트 데이터가 확보된 상태에서만 동작함.

- **변경 대상**: `server.py`, `prompts/weekly_report.md`
- **유형**: [리팩토링]
- **내용**:
  - **작업 요약**: AI 요약 생성용 프롬프트를 코드 내 하드코딩 방식에서 외부 파일(`prompts/weekly_report.md`) 로드 방식으로 변경
  - **수정 내용**:
    - 프로젝트 루트에 `prompts` 폴더 생성 및 `weekly_report.md` 템플릿 파일 작성
    - `server.py`의 `generate_ai_insights` 함수에서 프롬프트 템플릿을 파일에서 우선적으로 읽어오도록 수정
    - 템플릿 로드 우선순위: 파일 > .env 변수 > 하드코딩 기본값
  - **결과**: 프롬프트 수정 시 코드 재배포 없이 마크다운 파일만 수정하면 되므로 유지보수성 향상

- **변경 대상**: `server.py`, `dashboard/src/App.jsx`, `templates/prompt_manager.html`
- **유형**: [기능개선]
- **내용**:
  - **작업 요약**: 프롬프트 관리 기능을 모달 팝업에서 별도의 독립된 페이지로 변경
  - **수정 내용**:
    - `server.py`: `/prompt-manager` 엔드포인트 추가 (HTML 페이지 서빙)
    - `templates/prompt_manager.html`: 프롬프트 편집을 위한 전용 HTML 템플릿 생성 (Tailwind CSS 적용)
    - `App.jsx`: '프롬프트 관리' 버튼 클릭 시 새 탭에서 관리 페이지를 열도록 수정, 기존 모달 컴포넌트 제거
  - **결과**: 더 넓은 화면에서 쾌적하게 프롬프트를 편집할 수 있으며, 수신자 관리와 일관된 UX 제공
