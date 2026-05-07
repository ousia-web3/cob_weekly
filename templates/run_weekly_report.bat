@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo [1/2] 주간 리포트 생성 (generate_email_report.py)
echo ========================================
call venv\Scripts\activate
python generate_email_report.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] 리포트 생성 중 오류가 발생했습니다.
    echo 창을 닫지 않고 대기합니다...
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================
echo [2/2] 이메일 발송 (send_weekly_report_email.py)
echo ========================================
python send_weekly_report_email.py

echo.
echo 모든 작업이 완료되었습니다.
pause
