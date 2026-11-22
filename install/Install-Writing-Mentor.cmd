@echo off
rem Writing Mentor setup for Windows. Double-click to install or update.
rem If Windows shows "Windows protected your PC", click "More info", then "Run anyway".
title Writing Mentor setup
setlocal
if defined WMF_SOURCE (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%WMF_SOURCE%\install\install.ps1"
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $s = Invoke-RestMethod 'https://raw.githubusercontent.com/Black-JL/writing-mentor-framework/main/install/install.ps1'; & ([scriptblock]::Create($s))"
)
set "CODE=%ERRORLEVEL%"
if not defined CI (
    echo.
    pause
)
exit /b %CODE%
