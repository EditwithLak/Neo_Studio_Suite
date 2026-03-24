@echo off
setlocal

cd /d "%~dp0\.."

set "HOST=127.0.0.1"
set "PORT=8000"
set "URL=http://%HOST%:%PORT%"
if not defined KOBOLDCPP_BASE_URL set "KOBOLDCPP_BASE_URL=http://localhost:5001"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else if exist "neo_studio_v1\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=neo_studio_v1\.venv\Scripts\python.exe"
) else if exist "neo_studio_v1\venv\Scripts\python.exe" (
    set "PYTHON_EXE=neo_studio_v1\venv\Scripts\python.exe"
) else (
    where py >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_EXE=py"
    ) else (
        set "PYTHON_EXE=python"
    )
)

echo Checking environment...
%PYTHON_EXE% -c "import uvicorn, fastapi, jinja2, multipart, httpx, PIL" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Missing required packages.
    echo Please install them first, for example:
    echo pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Starting Neo Studio on %URL%
echo Backend base URL: %KOBOLDCPP_BASE_URL%
start "" "%URL%"
%PYTHON_EXE% -m uvicorn neo_studio_v1.app:app --host %HOST% --port %PORT%

echo.
echo Neo Studio stopped.
pause
endlocal
