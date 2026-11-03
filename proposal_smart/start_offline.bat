@echo off
title 스마트 제안서 생성 서버 (오프라인)
cd /d "%~dp0"
echo ================================================================
echo  스마트 제안서 자동 생성 - 오프라인 실행 (인터넷 불필요)
echo ================================================================
where python >nul 2>nul
if errorlevel 1 (
  echo [오류] 파이썬이 없습니다. 같이 넣어 둔 python 설치파일이 없으면 IT 에 Python 3.11 이상 설치를 요청하세요.
  pause & exit /b 1
)
echo [1/3] 패키지를 같이 넣어 둔 wheels 폴더에서 설치합니다 (인터넷 안 씀)
python -c "import pdfplumber, fitz, pypdf, reportlab, playwright, PIL" >nul 2>nul
if not errorlevel 1 (
  echo        이미 설치되어 있어 건너뜁니다.
) else (
  python -m pip install --disable-pip-version-check -q --no-index --find-links wheels pdfplumber "pymupdf<1.26" pypdf reportlab playwright pillow openpyxl
  if errorlevel 1 (
    echo [오류] wheels 설치 실패. 파이썬 판이 3.11~3.13 인지 확인하세요 :  python --version
    pause & exit /b 1
  )
)
echo [2/3] PDF 만드는 브라우저 : 노트북의 Edge 또는 Chrome 을 그대로 씁니다
set GA_CHROMIUM=
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "GA_CHROMIUM=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "GA_CHROMIUM=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "GA_CHROMIUM=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "GA_CHROMIUM=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if "%GA_CHROMIUM%"=="" (
  echo [오류] Edge 나 Chrome 을 찾지 못했습니다. 둘 중 하나가 깔려 있어야 합니다.
  pause & exit /b 1
)
echo        사용 : %GA_CHROMIUM%
echo [3/3] 서버를 켭니다. 잠시 뒤 브라우저가 열립니다. 끝내려면 이 창에서 Ctrl+C
start "" cmd /c "timeout /t 4 >nul & start "" http://127.0.0.1:8080/"
python api.py
pause
