@echo off
echo ========================================
echo   VisaSight Fresh Restart Script
echo ========================================
echo.

echo [1/3] Stopping any existing servers...
echo Please press Ctrl+C in all terminal windows first, then press any key here to continue.
pause
echo.

echo [2/3] Clearing Next.js build cache...
cd frontend
if exist .next rmdir /s /q .next
echo Build cache cleared!
echo.

echo [3/3] Instructions for manual restart:
echo.
echo TERMINAL 1 (Backend):
echo   cd backend
echo   python -m uvicorn main:app --reload --port 8000
echo.
echo TERMINAL 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo After starting both terminals, wait 10 seconds, then open:
echo   http://localhost:3000
echo.
echo Press Ctrl+Shift+F5 in your browser to force refresh!
echo ========================================
pause
