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
  echo        https://www.python.org/downloads/ 에서 Python 3.10 이상을 설치할 때
  echo        설치 화면의 "Add python.exe to PATH" 를 체크해 주세요.
  echo.
  pause
  exit /b 1
)

echo [1/3] 필요한 패키지를 확인합니다
python -c "import pdfplumber, fitz, pypdf, reportlab, playwright, PIL" >nul 2>nul
if not errorlevel 1 (
  echo        이미 설치되어 있습니다. 설치 단계를 건너뜁니다.
  goto :chromium
)
echo        처음 한 번만 설치합니다 (몇 분 걸립니다)
python -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
  echo.
  echo [오류] 패키지 설치에 실패했습니다. 사내망에서는 프록시 때문에 pip 가 막힐 수 있습니다.
  echo        아래 둘 중 하나로 해결합니다.
  echo        1) 사내 프록시 주소를 알면 이 창에 입력 :  set HTTPS_PROXY=http://프록시주소:포트
  echo           그리고 다시 실행 :  python -m pip install --proxy %%HTTPS_PROXY%% --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
  echo        2) 인터넷이 되는 PC 에서 wheels 폴더를 받아 와 설치 :  python -m pip install --no-index --find-links wheels -r requirements.txt
  echo           (wheels 폴더 만드는 법 : python -m pip download -r requirements.txt -d wheels --platform win_amd64 --only-binary=:all: --python-version 3.11)
  echo.
  pause
  exit /b 1
)

:chromium
echo [2/3] PDF 만드는 브라우저를 확인합니다
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); b.close(); p.stop()" >nul 2>nul
if not errorlevel 1 (
  echo        이미 준비되어 있습니다.
  goto :run
)
python -m playwright install chromium
if errorlevel 1 (
  echo [오류] Chromium 설치에 실패했습니다. 사내망이면 프록시 설정 뒤 다시 실행하거나,
  echo        인터넷이 되는 PC 에서 %%USERPROFILE%%\AppData\Local\ms-playwright 폴더를 통째로 복사해 오면 됩니다.
  pause
  exit /b 1
)

:run
echo [3/3] 서버를 켭니다. 잠시 뒤 브라우저가 자동으로 열립니다.
echo        이 창을 닫으면 서버가 꺼집니다. 끝내려면 Ctrl+C 를 누르세요.
echo.
start "" cmd /c "timeout /t 4 >nul & start "" http://127.0.0.1:8080/"
python api.py

echo.
echo 서버가 종료되었습니다.
pause
