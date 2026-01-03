@echo off
echo ========================================
echo Starting n8n (No Docker Required)
echo ========================================
echo.

echo [1/3] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js is installed!
echo.

echo [2/3] Clearing npm cache (fixing potential lock issues)...
npm cache clean --force >nul 2>&1
echo Cache cleared!
echo.

echo [3/3] Starting n8n...
echo.
echo n8n will start at: http://localhost:5678
echo.
echo Keep this window open while using n8n.
echo Press Ctrl+C to stop.
echo.
echo ========================================
echo.

REM Start n8n using npx with --yes flag and ignore peer dependency warnings
REM Try with legacy peer deps first to avoid lock issues
npx --yes --legacy-peer-deps n8n

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Standard method failed. Trying alternative...
    echo ========================================
    echo.
    echo Attempting to install n8n globally...
    echo This may take a few minutes...
    echo.
    npm install -g n8n --legacy-peer-deps
    
    if %errorlevel% equ 0 (
        echo.
        echo Installation successful! Starting n8n...
        echo.
        n8n start
    ) else (
        echo.
        echo ========================================
        echo ERROR: Failed to start n8n!
        echo ========================================
        echo.
        echo Try these solutions:
        echo.
        echo Solution 1: Use alternative script
        echo   n8n\start_n8n_alternative.bat
        echo.
        echo Solution 2: Manual global install
        echo   npm install -g n8n --legacy-peer-deps
        echo   n8n start
        echo.
        echo Solution 3: Update npm first
        echo   npm install -g npm@latest
        echo   npm install -g n8n
        echo   n8n start
        echo.
        pause
        exit /b 1
    )
)

