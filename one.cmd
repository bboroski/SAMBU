@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0one.py" %*
) else (
    python "%~dp0one.py" %*
)
set "rc=%errorlevel%"
if not "%rc%"=="0" (
    echo.
    echo One-knob workflow failed with exit code %rc%.
    pause
) else if "%~1"=="" (
    echo.
    pause
)
exit /b %rc%
