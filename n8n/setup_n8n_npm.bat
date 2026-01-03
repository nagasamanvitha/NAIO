@echo off
echo ========================================
echo Naio n8n Setup Script (No Docker)
echo ========================================
echo.

echo [1/5] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ERROR: Node.js is not installed!
    echo ========================================
    echo.
    echo Please install Node.js first:
    echo   1. Download from: https://nodejs.org/
    echo   2. Install the LTS version
    echo   3. Restart your terminal
    echo   4. Run this script again
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo Node.js is installed: %NODE_VERSION%
echo.

echo [2/5] Checking npm installation...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed!
    echo This should come with Node.js. Please reinstall Node.js.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo npm is installed: %NPM_VERSION%
echo.

echo [3/5] Starting n8n with npx...
echo.
echo This will:
echo   - Download n8n automatically (first time only)
echo   - Start n8n on http://localhost:5678
echo   - Keep running until you press Ctrl+C
echo.
echo ========================================
echo IMPORTANT: Keep this window open!
echo ========================================
echo.
echo n8n will be available at: http://localhost:5678
echo.
echo Press Ctrl+C to stop n8n when you're done.
echo.
echo ========================================
echo.

echo [4/5] Clearing npm cache (preventing lock issues)...
npm cache clean --force >nul 2>&1
echo Cache cleared!
echo.

echo [5/5] Starting n8n with npx...
echo.
echo This will:
echo   - Download n8n automatically (first time only)
echo   - Start n8n on http://localhost:5678
echo   - Keep running until you press Ctrl+C
echo.
echo ========================================
echo IMPORTANT: Keep this window open!
echo ========================================
echo.
echo n8n will be available at: http://localhost:5678
echo.
echo Press Ctrl+C to stop n8n when you're done.
echo.
echo ========================================
echo.

REM Start n8n using npx (no installation needed)
npx --yes n8n

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ERROR: Failed to start n8n!
    echo ========================================
    echo.
    echo This could be because:
    echo   1. Port 5678 is already in use
    echo   2. Network connection issues
    echo.
    echo To check if port 5678 is in use:
    echo   netstat -ano | findstr :5678
    echo.
    echo To use a different port, run manually:
    echo   npx -y n8n --port 5679
    echo.
    pause
    exit /b 1
)

