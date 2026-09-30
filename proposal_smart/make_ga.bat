@echo off
title GA 스마트 제안서 만들기
cd /d "%~dp0"

echo ================================================================
echo  GA 스마트 제안서 만들기
echo   - 설계서 PDF 를 이 파일(make_ga.bat) 위에 끌어다 놓으면 바로 만듭니다.
echo   - 그냥 두 번 누르면 ga_input 폴더에 넣어 둔 PDF 를 모두 만듭니다.
echo   - 결과는 ga_output 폴더에 PDF 와 로그(빈칸 이유)로 생깁니다.
echo ================================================================
echo.

where python >nul 2>nul
if errorlevel 1 goto nopython

if exist ".ga_ready" goto run
echo [준비] 처음 한 번만 필요한 프로그램을 설치합니다. 몇 분 걸립니다.
python -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto failpip
python -m playwright install chromium
if errorlevel 1 goto failchrome
echo ok> .ga_ready
echo [준비] 완료
echo.

:run
if "%~1"=="" goto folder
python ga_proposal.py %*
goto done

:folder
if not exist "ga_input" mkdir "ga_input"
python ga_proposal.py "%~dp0ga_input"
goto done

:done
if exist "ga_output" start "" "%~dp0ga_output"
echo.
pause
exit /b 0

:nopython
echo [오류] 파이썬이 설치되어 있지 않습니다.
echo        https://www.python.org/downloads/ 에서 Python 3.10 이상을 설치할 때
echo        설치 화면의 "Add python.exe to PATH" 를 체크해 주세요.
pause
exit /b 1

:failpip
echo [오류] 패키지 설치에 실패했습니다. 사내망 프록시 설정이 필요할 수 있습니다.
pause
exit /b 1

:failchrome
echo [오류] PDF 변환용 크로미엄 설치에 실패했습니다. 사내망 프록시 설정이 필요할 수 있습니다.
pause
exit /b 1
