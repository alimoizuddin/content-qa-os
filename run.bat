@echo off
rem LinkedIn Content Studio. Double-click this file to start the app.
rem The first time, it sets itself up and asks for your key. After that it just starts.
setlocal
cd /d "%~dp0"
title LinkedIn Content Studio

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed on this computer.
  echo Install it from https://www.python.org/downloads/ and tick
  echo "Add python.exe to PATH" during setup. Then double-click run.bat again.
  pause
  exit /b 1
)

if not exist "venv\Scripts\python.exe" (
  echo First run: setting up. This takes a few minutes and only happens once.
  python -m venv venv || goto :failed
  "venv\Scripts\python.exe" -m pip install --quiet --upgrade pip || goto :failed
  "venv\Scripts\python.exe" -m pip install --quiet -r requirements.lock || goto :failed
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo A settings file called .env has been created and will now open in Notepad.
  echo Paste your NVIDIA key after NVIDIA_API_KEY= then save and close Notepad.
  echo Then double-click run.bat again.
  notepad ".env"
  pause
  exit /b 0
)

echo Starting the app. Your browser will open in a few seconds.
echo Keep this window open while you use the app. Close it to stop the app.
if not defined NO_BROWSER start "" /min powershell -NoProfile -Command "Start-Sleep -Seconds 6; Start-Process 'http://127.0.0.1:8501'"
"venv\Scripts\python.exe" -m streamlit run app.py
goto :eof

:failed
echo.
echo Setup did not finish. Check your internet connection and double-click run.bat again.
pause
exit /b 1
