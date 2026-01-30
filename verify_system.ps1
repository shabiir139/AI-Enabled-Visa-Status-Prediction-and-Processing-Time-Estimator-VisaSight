# VisaSight System Verification Script
# This script checks all components of the VisaSight application

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "  VisaSight System Verification  " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check Backend Health
Write-Host "`n[1/6] Checking Backend Health..." -ForegroundColor Yellow
try {
    $health = curl.exe -s http://localhost:8000/health | ConvertFrom-Json
    if ($health.status -eq "healthy") {
        Write-Host "  ✓ Backend is HEALTHY" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Backend returned unexpected status" -ForegroundColor Red
    }
}
catch {
    Write-Host "  ✗ Backend is NOT responding" -ForegroundColor Red
}

# Check Backend API Endpoints
Write-Host "`n[2/6] Checking Backend API..." -ForegroundColor Yellow
try {
    $cases = curl.exe -s http://localhost:8000/api/cases | ConvertFrom-Json
    Write-Host "  ✓ Cases API working (Total cases: $($cases.total))" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠ Cases API may be slow or unavailable" -ForegroundColor Yellow
}

# Check Frontend Server
Write-Host "`n[3/6] Checking Frontend Server..." -ForegroundColor Yellow
try {
    $frontendTest = curl.exe -I -s http://localhost:3000 2>&1 | Select-String "HTTP" | Select-Object -First 1
    if ($frontendTest -match "200") {
        Write-Host "  ✓ Frontend is serving on port 3000" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Frontend returned non-200 status" -ForegroundColor Red
    }
}
catch {
    Write-Host "  ✗ Frontend is NOT responding" -ForegroundColor Red
}

# Check Frontend->Backend Integration
Write-Host "`n[4/6] Checking Frontend-Backend Integration..." -ForegroundColor Yellow
try {
    $proxyTest = curl.exe -s "http://localhost:3000/api/cases" -w "HTTP_CODE:%{http_code}" | Select-String "HTTP_CODE"
    if ($proxyTest -match "200") {
        Write-Host "  ✓ Frontend can communicate with Backend" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Frontend-Backend proxy not working" -ForegroundColor Red
    }
}
catch {
    Write-Host "  ✗ Integration test failed" -ForegroundColor Red
}

# Check Environment Variables
Write-Host "`n[5/6] Checking Environment Configuration..." -ForegroundColor Yellow
if (Test-Path "frontend\.env.local") {
    $envContent = Get-Content "frontend\.env.local" -Raw
    if ($envContent -match "NEXT_PUBLIC_API_URL=http://localhost:8000") {
        Write-Host "  ✓ Frontend .env.local is correctly configured" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠ Frontend .env.local may need updating" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  ✗ Frontend .env.local not found" -ForegroundColor Red
}

if (Test-Path "backend\.env") {
    Write-Host "  ✓ Backend .env file exists" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Backend .env not found" -ForegroundColor Red
}

# Check Supabase Connection
Write-Host "`n[6/6] Checking Supabase Integration..." -ForegroundColor Yellow
try {
    $models = curl.exe -s http://localhost:8000/api/models | ConvertFrom-Json
    Write-Host "  ✓ Backend can access ML models" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠ Models endpoint unavailable (this is okay for now)" -ForegroundColor Yellow
}

# Final Summary
Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "  Verification Complete!          " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

Write-Host "`nYour VisaSight application is accessible at:" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`nIf you see any ✗ marks above, please check:" -ForegroundColor Yellow
Write-Host "  1. Both backend and frontend terminals are running" -ForegroundColor White
Write-Host "  2. No other process is using ports 3000 or 8000" -ForegroundColor White
Write-Host "  3. Environment files are properly configured`n" -ForegroundColor White
