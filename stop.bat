@echo off
chcp 65001 > nul
echo 서버 프로세스를 종료합니다...

taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo.
echo 모든 서버가 종료되었습니다.
echo 창을 닫으셔도 됩니다.
timeout /t 3 > nul
