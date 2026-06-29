@echo off
chcp 65001 >nul
title 🔬 Lancement Cheat Engine + MCP

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║   🔬 Lancement Cheat Engine avec MCP Bridge                      ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Chercher Cheat Engine
set CE_PATH=

if exist "C:\Program Files\Cheat Engine 7.5\cheatengine-x86_64.exe" (
    set CE_PATH=C:\Program Files\Cheat Engine 7.5\cheatengine-x86_64.exe
)
if exist "C:\Program Files\Cheat Engine 7.6\cheatengine-x86_64.exe" (
    set CE_PATH=C:\Program Files\Cheat Engine 7.6\cheatengine-x86_64.exe
)
if exist "C:\Program Files (x86)\Cheat Engine 7.5\cheatengine-x86_64.exe" (
    set CE_PATH=C:\Program Files (x86)\Cheat Engine 7.5\cheatengine-x86_64.exe
)

if "%CE_PATH%"=="" (
    echo ❌ Cheat Engine non trouvé !
    echo.
    echo    Télécharge-le sur : https://www.cheatengine.org/downloads.php
    echo.
    pause
    exit /b 1
)

echo ✅ Cheat Engine trouvé: %CE_PATH%
echo.
echo 📋 Instructions:
echo.
echo    1. Cheat Engine va s'ouvrir
echo    2. File → Open Process → eldenring.exe
echo    3. File → Execute Script → Colle ce chemin:
echo.
echo    %~dp0tools\cheatengine-mcp\MCP_Server\ce_mcp_bridge.lua
echo.
echo    4. Clique Execute
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.

:: Copier le chemin dans le presse-papier
echo %~dp0tools\cheatengine-mcp\MCP_Server\ce_mcp_bridge.lua | clip
echo 📋 Chemin copié dans le presse-papier !
echo.

:: Lancer Cheat Engine
echo 🚀 Lancement de Cheat Engine...
start "" "%CE_PATH%"

echo.
echo ✅ Cheat Engine lancé !
echo.
echo    Quand tu vois "[MCP] Server started" dans CE, 
echo    relance TEMPLE_IAM.bat pour utiliser le mode CHEAT !
echo.
pause

