@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "CONDA_EXE=D:\app\Anaconda\Scripts\conda.exe"
set "CONDA_ENV=NasPortal"

if not exist ".env" (
    echo [ERROR] .env was not found.
    exit /b 1
)

if not exist "%CONDA_EXE%" (
    echo [ERROR] Conda was not found at %CONDA_EXE%.
    exit /b 1
)

set "ENV_MODE="
for /f "usebackq tokens=1,* delims==" %%A in (`findstr /b "ENV=" ".env"`) do (
    set "ENV_MODE=%%B"
)

set "ENV_MODE=%ENV_MODE:"=%"

if not defined ENV_MODE (
    echo [ERROR] ENV is missing in .env. Use ENV=DEV or ENV=PRD.
    exit /b 1
)

if /I "%ENV_MODE%"=="DEV" (
    echo [INFO] Starting NasPortal in DEV mode with hot reload...
    "%CONDA_EXE%" run -n %CONDA_ENV% python run.py admin ensure --username admin --password admin
    "%CONDA_EXE%" run -n %CONDA_ENV% python run.py rundev --host 127.0.0.1 --port 8000 --reload
    exit /b %ERRORLEVEL%
)

if /I "%ENV_MODE%"=="PRD" (
    echo [INFO] Starting NasPortal in PRD mode...
    "%CONDA_EXE%" run -n %CONDA_ENV% python run.py runprd --host 0.0.0.0 --port 8000 --workers 1
    exit /b %ERRORLEVEL%
)

echo [ERROR] Unsupported ENV value "%ENV_MODE%". Use DEV or PRD.
exit /b 1
