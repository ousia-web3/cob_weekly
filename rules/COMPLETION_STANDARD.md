# 완료 기준 (Completion Standard)

이 문서는 **2026-03-04 현재 작업 완료 기준**으로, 이후 수정 시 반드시 유지해야 할 사항을 정의합니다.

## 1. AI 요약 수정 기능 (필수 유지)

### 1.1 기능 요구사항
- **수정 버튼**: 기생성된 AI 요약을 편집 모드로 전환
- **편집 모드에서 지원**:
  - **수정**: 제목·내용 수정 가능
  - **추가**: 새 인사이트 항목 추가 (추가 버튼)
  - **삭제**: 각 항목별 삭제 버튼으로 제거
- **저장/취소**: 변경사항 저장 또는 취소 후 보기 모드로 복귀

### 1.2 데이터 구조 (불변)
- `aiInsight` 형식: `Array<{ title: string, content: string }>`
- `title`, `content`는 반드시 **문자열**이어야 함 (input/textarea value 호환)

### 1.3 영향 받는 파일
- `dashboard/src/components/DashboardPreview.jsx`: 수정/추가/삭제 UI 및 로직
- `dashboard/src/App.jsx`: `handleInsightsChange`, `onInsightsChange` 연결
- `dashboard/src/utils/exportUtils.js`: HTML 내보내기 시 aiInsight 사용
- `generate_email_report.py`: 이메일 템플릿 생성 시 `aiInsight` 사용

## 2. 방어 로직 (필수 유지)

- `handleEditInsights`: `aiInsight`를 `String(i?.title ?? '')`, `String(i?.content ?? '')` 형태로 정규화
- input/textarea: `value={String(insight?.title ?? '')}` 등으로 항상 문자열 보장
- `coBrandTop20`, `categories`: `?? []` 등 null-safe 처리
- `top20SumUV` 0 나눗셈 방지

## 3. Error Boundary (필수 유지)

- `dashboard/src/components/ErrorBoundary.jsx`: 에러 포착 시 화면에 에러 메시지 표시
- `main.jsx`: 앱 최상위 `ErrorBoundary` 래핑 유지
- `App.jsx`: `DashboardPreview` 주변 `ErrorBoundary` 래핑 유지

## 4. 참고 규칙

- 이 기준은 `rules/CHANGELOG.md` 2026-03-04 항목과 연계됩니다.
- 수정 시 `aiInsight`의 `{ title, content }` 구조와 호환성을 유지해야 합니다.
