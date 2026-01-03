@echo off
echo ========================================
echo Installing n8n Globally (Optional)
echo ========================================
echo.
echo This will install n8n globally so you can use 'n8n' command directly.
echo This is optional - you can also use 'npx n8n' without installing.
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

echo [2/3] Installing n8n globally...
echo This may take a few minutes...
npm install -g n8n

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ERROR: Installation failed!
    echo ========================================
    echo.
    echo You can still use n8n without global installation:
    echo   npx -y n8n
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Installation complete!
echo.
echo ========================================
echo n8n is now installed globally!
echo ========================================
echo.
echo You can now start n8n with:
echo   n8n start
echo.
echo Or continue using:
echo   npx -y n8n
echo.
echo n8n will be available at: http://localhost:5678
echo.
pause







