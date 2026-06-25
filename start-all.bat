@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_PYTHON=%BACKEND_DIR%\venv\Scripts\python.exe"

if not exist "%BACKEND_PYTHON%" (
    echo [ERROR] Missing backend venv: %BACKEND_PYTHON%
    echo Run backend setup first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [ERROR] Missing frontend dependencies: %FRONTEND_DIR%\node_modules
    echo Run frontend setup first:
    echo   cd frontend
    echo   npm install
    exit /b 1
)

if not exist "%BACKEND_DIR%\.env" if exist "%BACKEND_DIR%\.env.example" (
    copy /y "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
    echo [INFO] Created backend\.env from .env.example
)

start "Linji API" cmd /k "cd /d ""%BACKEND_DIR%"" && ""%BACKEND_PYTHON%"" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
start "Linji QQ Group Bot" cmd /k "cd /d ""%BACKEND_DIR%"" && ""%BACKEND_PYTHON%"" -m app.workers.qq_group_bot"
start "Linji Reminder Worker" cmd /k "cd /d ""%BACKEND_DIR%"" && ""%BACKEND_PYTHON%"" -m app.workers.reminder_summary_worker"
start "Linji Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"

echo [OK] Started API, QQ bot, reminder worker, and frontend in separate windows.
echo [INFO] Frontend: http://127.0.0.1:5173
echo [INFO] Backend:  http://127.0.0.1:8000
