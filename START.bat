@echo off
title ChainKYC - Blockchain KYC Verification
color 0A

echo.
echo  ===============================================
echo    ___ _         _       _  ___   _____ 
echo   / __| |_  __ _(_)_ __ ^| ^|/ ^| ^\ / / __|
echo  ^| (__^| ' \/ _` ^| ^| '  \^|   ^< \ V / (__ 
echo   \___^|_^|_\__,_^|_^|_^|_^|_^|_^|\_\ ^|_^| \___^|
echo.     
echo   Blockchain-based Secure KYC Verification
echo   6th Sem BT Mini Project - Mumbai University
echo  ===============================================
echo.

REM Check if Python is available for a local HTTP server
where python >nul 2>nul
if %ERRORLEVEL%==0 (
    echo  [*] Starting local server at http://localhost:8000
    echo  [*] Press Ctrl+C to stop the server
    echo.
    echo  Opening browser...
    timeout /t 2 /nobreak >nul
    start http://localhost:8000/index.html
    echo.
    echo  -----------------------------------------------
    echo   Server running. Keep this window open.
    echo   Close this window to stop the server.
    echo  -----------------------------------------------
    echo.
    python -m http.server 8000
) else (
    echo  [!] Python not found - opening file directly.
    echo  [!] Some features may not work without a server.
    echo.
    start "" "%~dp0index.html"
    echo  Opened index.html in your default browser.
    echo.
    pause
)
