@echo off
chcp 65001 > nul
echo ========================================
echo 코브랜드 주간 현황 대시보드 시작
echo ========================================
echo.

echo [1/2] 백엔드 서버 시작 중...
start "Backend Server" cmd /k "call venv\Scripts\activate && python server.py"
timeout /t 3 /nobreak > nul
echo ✓ 백엔드 서버 시작됨 (포트 8001)
echo.

echo [2/2] 프론트엔드 서버 시작 중...
start "Frontend Server" cmd /k "cd dashboard && npm run dev"
timeout /t 2 /nobreak > nul
echo ✓ 프론트엔드 서버 시작됨
echo.

echo ========================================
echo 모든 서버가 시작되었습니다!
echo 백엔드: http://localhost:8001
echo 프론트엔드: http://localhost:5173 / http://192.168.82.105:5173
echo ========================================
echo.

echo [3/3] 크롬 브라우저 실행 중...
timeout /t 5 /nobreak > nul
start chrome http://localhost:5173
echo ✓ 브라우저가 열렸습니다
echo.

echo 종료하려면 stop.bat 파일을 실행하세요.
echo.
pause
