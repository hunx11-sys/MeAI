@echo off
title GA 스마트 제안서 (오프라인)
cd /d "%~dp0"
set GA_CHROMIUM=
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "GA_CHROMIUM=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "GA_CHROMIUM=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "GA_CHROMIUM=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
python -c "import pdfplumber, fitz, pypdf, reportlab, playwright, PIL" >nul 2>nul || python -m pip install --disable-pip-version-check -q --no-index --find-links wheels pdfplumber "pymupdf<1.26" pypdf reportlab playwright pillow openpyxl
if not exist ga_input mkdir ga_input
if "%~1"=="" (
  echo 설계서 PDF 를 ga_input 폴더에 넣고 다시 실행하거나, 이 파일 위에 PDF 를 끌어다 놓으세요.
  python ga_proposal.py ga_input
) else (
  for %%F in (%*) do python ga_proposal.py "%%~F"
)
pause
