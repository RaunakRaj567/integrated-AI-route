# start.ps1
Write-Host "=======================================================================" -ForegroundColor Green
Write-Host "   AGRI-LOGISTICS PROFIT OPTIMIZATION & ROUTING PORTAL" -ForegroundColor Green
Write-Host "=======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Launching FastAPI Backend (Port 8000) and React Frontend (Port 5173)..." -ForegroundColor Cyan
Write-Host ""

python run.py
