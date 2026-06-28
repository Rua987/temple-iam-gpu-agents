@echo off
chcp 65001 >nul
title ODIN VISION - Dashboard Web

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   👁️ ODIN VISION - Dashboard Web                                ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo   🚀 Démarrage du serveur...
echo.

cd /d "%~dp0agents\odin_vision"
python odin_web.py

pause

