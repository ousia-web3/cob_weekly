@echo off
chcp 65001 > nul
echo ========================================
echo 코브랜드 주간 현황 대시보드 종료
echo ========================================
echo.

echo [1/2] 백엔드 서버 종료 중...
taskkill /FI "WindowTitle eq Backend Server*" /T /F > nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 백엔드 서버 종료됨
) else (
    echo ⚠ 백엔드 서버를 찾을 수 없습니다
)
echo.

echo [2/2] 프론트엔드 서버 종료 중...
taskkill /FI "WindowTitle eq Frontend Server*" /T /F > nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 프론트엔드 서버 종료됨
) else (
    echo ⚠ 프론트엔드 서버를 찾을 수 없습니다
)
echo.

echo Python 프로세스 정리 중...
taskkill /IM python.exe /F > nul 2>&1
echo.

echo Node 프로세스 정리 중...
taskkill /IM node.exe /F > nul 2>&1
echo.

echo ========================================
echo 모든 서버가 종료되었습니다!
echo ========================================
echo.
pause
