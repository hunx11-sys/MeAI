@echo off
title 스마트 제안서 생성 서버
cd /d "%~dp0"

echo ================================================================
echo  스마트 제안서 자동 생성 - 서버 시작
echo ================================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [오류] 파이썬이 설치되어 있지 않습니다.
  echo        https://www.python.org/downloads/ 에서 Python 3.10 이상을 설치한 뒤
  echo        설치 화면의 "Add python.exe to PATH" 를 체크해 주세요.
  echo.
  pause
  exit /b 1
)

echo [1/3] 필요한 패키지를 확인합니다 (처음 한 번만 몇 분 걸립니다)
python -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
  echo [오류] 패키지 설치에 실패했습니다. 사내망 프록시 설정이 필요할 수 있습니다.
  pause
  exit /b 1
)

echo [2/3] PDF 렌더용 브라우저를 확인합니다
python -m playwright install chromium
if errorlevel 1 (
  echo [오류] Chromium 설치에 실패했습니다.
  pause
  exit /b 1
)

echo [3/3] 서버를 켭니다. 잠시 뒤 브라우저가 자동으로 열립니다.
echo        이 창을 닫으면 서버가 꺼집니다. 종료할 때는 Ctrl+C 를 누르세요.
echo.
start "" cmd /c "timeout /t 4 >nul & start "" http://127.0.0.1:8080/"
python api.py

echo.
echo 서버가 종료되었습니다.
pause
