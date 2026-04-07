@echo off
color 0A
title FileSure Project Launcher

echo =======================================================
echo          Starting FileSure Project
echo =======================================================
echo.

echo [1/3] Loading Data into Database (Python)...
echo Please wait, this might take a minute...
cd ingestion
call pip install -r requirements.txt
call python ingest.py
cd ..

echo.
echo [2/3] Installing API Dependencies (Node.js)...
cd api
call npm install

echo.
echo Starting the background API Server...
:: Opens a new window that stays open to run the API
start "FileSure API Server" cmd /k "echo Do not close this window! It is running the API Database Bridge. && echo. && node index.js"
cd ..

echo.
echo [3/3] Opening dashboard in your default browser...
:: Wait 3 seconds to let the API start up properly before opening the browser
timeout /t 3 /nobreak > NUL
start "" "%~dp0frontend\index.html"

echo.
echo =======================================================
echo All done! The dashboard should be open in your browser.
echo You may close this current green window, 
echo but do NOT close the other black API window!
echo =======================================================
echo.
pause
