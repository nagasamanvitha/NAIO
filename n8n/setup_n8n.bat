@echo off
echo ========================================
echo Naio n8n Setup Script
echo ========================================
echo.

echo [1/5] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed!
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo Docker is installed!
echo.

echo [2/5] Checking if Docker Desktop is running...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ERROR: Docker Desktop is not running!
    echo ========================================
    echo.
    echo Please start Docker Desktop first:
    echo.
    echo Option 1: Start Menu
    echo   1. Press Windows Key
    echo   2. Type "Docker Desktop"
    echo   3. Click "Docker Desktop"
    echo.
    echo Option 2: Desktop Shortcut
    echo   - Double-click the Docker Desktop icon on your desktop
    echo.
    echo Option 3: Run Command
    echo   Press Windows Key + R, then type:
    echo   "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo.
    echo After starting Docker Desktop:
    echo   1. Wait 30-60 seconds for it to fully initialize
    echo   2. Look for the Docker icon in your system tray (bottom right)
    echo   3. The icon should show "Docker Desktop is running" when ready
    echo.
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)
echo Docker Desktop is running!
echo.

echo [3/5] Checking if n8n is already running...
docker ps | findstr n8n >nul 2>&1
if %errorlevel% equ 0 (
    echo n8n is already running!
    echo.
    echo n8n URL: http://localhost:5678
    echo.
    echo Press any key to continue to next step...
    pause >nul
    goto :import_workflows
)

echo [4/5] Starting n8n container...
echo This will start n8n in the background.
echo n8n will be available at: http://localhost:5678
echo.
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ERROR: Failed to start n8n!
    echo ========================================
    echo.
    echo This could be because:
    echo   1. Docker Desktop is not running (see instructions above)
    echo   2. Port 5678 is already in use
    echo   3. A container named 'n8n' already exists
    echo.
    echo To check for existing containers, run:
    echo   docker ps -a
    echo.
    echo To remove an existing n8n container, run:
    echo   docker rm -f n8n
    echo.
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

echo n8n started successfully!
echo Waiting 5 seconds for n8n to initialize...
timeout /t 5 /nobreak >nul

:import_workflows
echo.
echo [5/5] n8n Setup Instructions:
echo.
echo 1. Open your browser and go to: http://localhost:5678
echo 2. Create an account (first time only)
echo 3. Click "Workflows" in the sidebar
echo 4. Click "Import from File" button
echo 5. Import these files:
echo    - n8n\workflows\zendesk_workflow.json
echo    - n8n\workflows\intercom_workflow.json
echo    - n8n\workflows\unified_workflow.json
echo.
echo [6/6] Upload Mock Data:
echo.
echo 1. In n8n, click "Files" in the sidebar
echo 2. Upload all CSV files from: n8n\mock_data\
echo    - zendesk_mock.csv
echo    - salesforce_mock.csv
echo    - nps_mock.csv
echo    - app_store_mock.csv
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Open n8n: http://localhost:5678
echo 2. Import workflows (see instructions above)
echo 3. Upload mock data files
echo 4. Configure workflows with your backend URL
echo 5. Execute workflows to test!
echo.
echo For detailed instructions, see: n8n\SETUP_GUIDE.md
echo.
pause


