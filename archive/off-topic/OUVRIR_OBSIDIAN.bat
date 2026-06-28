@echo off
chcp 65001 >nul
echo ========================================
echo 📝 OUVERTURE OBSIDIAN - TEMPLE IAM
echo ========================================
echo.

REM Vérifier si Obsidian est installé
where obsidian >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ Obsidian trouvé !
    echo.
    echo 🚀 Ouverture d'Obsidian avec ce dossier...
    echo.
    
    REM Essayer d'ouvrir avec Obsidian
    start "" obsidian://open?vault=%CD:~0,1%%CD:~2%
    
    REM Alternative : ouvrir Obsidian et laisser l'utilisateur sélectionner
    start "" obsidian:
    
    echo ✅ Obsidian devrait s'ouvrir !
    echo.
    echo 📝 Si Obsidian s'ouvre mais pas ce dossier :
    echo    1. Clique sur "Open folder as vault"
    echo    2. Sélectionne : %CD%
    echo    3. Clique sur "Open"
    echo.
    timeout /t 3 >nul
    exit /b 0
)

echo ❌ Obsidian n'est pas installé ou pas dans le PATH
echo.
echo 📥 Pour installer Obsidian :
echo    1. Lance INSTALL_OBSIDIAN.bat
echo    OU
echo    2. Va sur https://obsidian.md/download
echo.
pause

