@echo off
chcp 65001 >nul
cd /d "%~dp0"
where java >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Java 17+ is not installed or not in PATH.
  pause
  exit /b 1
)
echo Smart Proposal (Java) - http://127.0.0.1:8080  (stop: Ctrl+C)
java -Dfile.encoding=UTF-8 -jar smart-proposal.jar serve 127.0.0.1 8080
pause
