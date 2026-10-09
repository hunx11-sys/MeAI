@echo off
title MeAI홈 30초 영상 조립기
cd /d "%~dp0"
echo ================================================================
echo  MeAI홈 오픈 30초 영상 조립기
echo   - Higgsfield 에서 받은 영상을 clips 폴더에 정해진 이름으로 넣고 실행하세요.
echo   - 없는 장면은 임시 그림으로 채웁니다.
echo   - 결과 : out\meai_home_30s.mp4
echo ================================================================
where python >nul 2>nul
if errorlevel 1 goto nopython
if exist ".video_ready" goto run
echo [준비] 처음 한 번만 필요한 프로그램을 설치합니다.
python -m pip install --disable-pip-version-check -q pillow numpy imageio-ffmpeg
if errorlevel 1 goto failpip
echo ok> .video_ready
:run
python build_video.py %*
goto done
:nopython
echo [오류] 파이썬이 설치되어 있지 않습니다.
goto done
:failpip
echo [오류] 프로그램 설치에 실패했습니다. 인터넷 연결을 확인하세요.
:done
pause
