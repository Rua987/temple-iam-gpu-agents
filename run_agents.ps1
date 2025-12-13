# Temple IAM GPU Agents - PowerShell Launcher
# PLUS ULTRA ! DATTEBAYO !

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEMPLE IAM GPU AGENTS - MENU" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. GPU Monitor (Surveillance temps reel)" -ForegroundColor Green
Write-Host "2. Thermal Optimizer (Controle temperature)" -ForegroundColor Yellow
Write-Host "3. GPU Virtual Integration (Lance Alan Wake 2)" -ForegroundColor Magenta
Write-Host "4. Test GPU Quick (Validation systeme)" -ForegroundColor White
Write-Host "5. Tous les agents (Monitor + Thermal)" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Choisis une option (1-5)"

switch ($choice) {
    "1" {
        Write-Host "[*] Lancement GPU Monitor..." -ForegroundColor Green
        Write-Host "[*] Appuie sur Ctrl+C pour arreter" -ForegroundColor Yellow
        python run_gpu_monitor.py
    }
    "2" {
        Write-Host "[*] Lancement Thermal Optimizer..." -ForegroundColor Yellow
        Write-Host "[!] Necessite permissions admin pour modifier GPU" -ForegroundColor Red
        python temple_iam_thermal_optimizer.py
    }
    "3" {
        Write-Host "[*] Lancement GPU Virtual Integration..." -ForegroundColor Magenta
        Write-Host "[*] Va detecter et lancer Alan Wake 2" -ForegroundColor Cyan
        python temple_iam_alan_wake2_gpu_virtual_integration.py
    }
    "4" {
        Write-Host "[*] Lancement tests GPU..." -ForegroundColor White
        python test_gpu_quick.py
    }
    "5" {
        Write-Host "[*] Lancement de tous les agents..." -ForegroundColor Red
        Start-Process python -ArgumentList "run_gpu_monitor.py" -NoNewWindow
        Start-Sleep -Seconds 2
        Start-Process python -ArgumentList "temple_iam_thermal_optimizer.py"
        Write-Host "[OK] Agents lances !" -ForegroundColor Green
    }
    default {
        Write-Host "[!] Option invalide" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "PLUS ULTRA ! DATTEBAYO !" -ForegroundColor Cyan
