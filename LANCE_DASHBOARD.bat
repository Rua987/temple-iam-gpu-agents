@echo off
chcp 65001 >nul 2>&1
title Temple IAM Dashboard - Bun.js

echo ================================================================================
echo    TEMPLE IAM DASHBOARD - SERVEUR BUN.JS
echo ================================================================================
echo.

REM Verifier si Bun est installe
where bun >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Bun.js n'est pas installe !
    echo.
    echo Pour installer Bun.js :
    echo    1. Ouvre PowerShell en admin
    echo    2. Execute: irm bun.sh/install.ps1 ^| iex
    echo.
    echo    OU telecharge depuis: https://bun.sh
    echo.
    pause
    exit /b 1
)

echo [OK] Bun.js detecte
echo.
echo Demarrage du serveur dashboard...
echo.
echo URL Dashboard : http://localhost:3000
echo.
echo GARDE CETTE FENETRE OUVERTE !
echo Lance ensuite l'optimiseur Python (LANCE_OPTIMIZER.bat)
echo.
echo ================================================================================

cd /d "%~dp0"
bun run dashboard_server.ts

pause
