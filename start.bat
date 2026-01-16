@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo [1/2] 백엔드 서버 실행 (8001 포트)
echo ========================================
:: 필요한 라이브러리 자동 설치 후 실행
start "Backend" cmd /k "call venv\Scripts\activate & pip install matplotlib pandas openpyxl & python server.py"

echo.
echo ========================================
echo [2/2] 프론트엔드 서버 실행 (5173 포트)
echo ========================================
cd dashboard
start "Frontend" cmd /k "npm run dev"

echo.
echo 브라우저를 실행합니다...
timeout /t 4 /nobreak > nul
start chrome http://localhost:5173
