---
description: 주간 보고서 생성 및 발송 마스터 워크플로우
---

# 주간 보고서 자동화 마스터 관리자 (Master Manager)

이 워크플로우는 서버 실행부터 리포트 생성, 이메일 발송까지의 전체 과정을 관리합니다.
에이전트는 각 단계의 실행 결과를 모니터링하고 오류 발생 시 사용자에게 알립니다.

## 워크플로우 단계

1. **서버 실행 (백그라운드)**
   - `server.py`가 실행 중인지 확인하고, 실행되지 않았다면 백그라운드에서 실행합니다.

   ```bash
   # 서버 실행 확인 및 시작 (이미 실행 중이면 건너뜀)
   tasklist /FI "IMAGENAME eq python.exe" | findstr server.py || start /B python server.py
   ```

2. **주간 리포트 생성**
   - 최신 데이터를 기반으로 HTML 리포트를 생성합니다.
   - `generate_email_report.py` 스크립트를 실행합니다.

   ```bash
   python generate_email_report.py
   ```

3. **이메일 발송 (자동)**
   - 생성된 리포트를 수신자 목록에게 발송합니다.
   - `send_weekly_report_email.py` 스크립트를 실행합니다.

   ```bash
   python send_weekly_report_email.py
   ```

4. **결과 모니터링**
   - 각 단계의 로그를 확인하여 성공 여부를 검증합니다.
   - 오류 발생 시 `server_error.log` 또는 콘솔 출력을 분석합니다.

5. **실시간 터미널 모니터링 및 자동 복구 (Active Terminal Monitoring)**
   - **[중요]** 에이전트는 모든 명령어 실행 후 즉시 출력을 분석해야 합니다.
   - 오류 감지 시:
     1. 사용자에게 오류 내용을 즉시 보고합니다.
     2. `server_error.log`를 확인하여 상세 원인을 파악합니다.
     3. 가능한 경우 수정 제안을 하거나, 사용자의 승인을 얻어 '자동 수정(Self-Correction)' 워크플로우를 실행합니다.
   - 마치 사용자와 화면을 공유하듯, 현재 터미널 상태를 주기적으로 체크하여 "문제 없음" 또는 "조치 필요" 상태를 업데이트합니다.

---

### 팁 (Tip)

> [!TIP]
> **수신자 관리**: 수신자를 변경하려면 `data/recipients.json`을 수정하거나 `.env` 파일의 `EMAIL_RECIPIENTS`를 업데이트하세요.

> [!NOTE]
> **터미널 모니터링**: 에이전트는 이 터미널의 출력을 실시간으로 분석하고 있습니다. 오류가 발생하면 즉시 알려주세요.
