@echo off
REM Script de démarrage propre Windows - Force le rechargement complet

echo 🧹 Nettoyage cache Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo ✅ Cache nettoyé
echo.
echo 🚀 Lancement du moniteur GPU...
echo.

python run_universal_monitor_v2.py
