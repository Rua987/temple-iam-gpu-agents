@echo off
chcp 65001 >nul
echo ========================================
echo 📝 INSTALLATION OBSIDIAN POUR TEMPLE IAM
echo ========================================
echo.

REM Vérifier si Obsidian est déjà installé
where obsidian >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ Obsidian est déjà installé !
    echo.
    echo Pour ouvrir ton projet Temple IAM :
    echo 1. Lance Obsidian
    echo 2. Clique sur "Open folder as vault"
    echo 3. Sélectionne : %CD%
    echo.
    pause
    exit /b 0
)

echo 📥 Téléchargement d'Obsidian...
echo.

REM Créer un dossier temporaire
set TEMP_DIR=%TEMP%\obsidian_install
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM URL de téléchargement Obsidian Windows
set OBSIDIAN_URL=https://github.com/obsidianmd/obsidian-releases/releases/download/v1.7.3/Obsidian-1.7.3.exe
set INSTALLER=%TEMP_DIR%\Obsidian-Setup.exe

echo Téléchargement depuis GitHub...
echo URL: %OBSIDIAN_URL%
echo.

REM Télécharger avec PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%OBSIDIAN_URL%' -OutFile '%INSTALLER%' -UseBasicParsing}"

if not exist "%INSTALLER%" (
    echo ❌ Erreur lors du téléchargement
    echo.
    echo 📝 INSTRUCTIONS MANUELLES :
    echo.
    echo 1. Va sur : https://obsidian.md/download
    echo 2. Clique sur "Download for Windows"
    echo 3. Installe le fichier téléchargé
    echo 4. Lance Obsidian
    echo 5. Clique sur "Open folder as vault"
    echo 6. Sélectionne ce dossier : %CD%
    echo.
    pause
    exit /b 1
)

echo ✅ Téléchargement terminé !
echo.
echo 📦 Fichier : %INSTALLER%
echo.
echo 🚀 Lancement de l'installateur...
echo.
echo ⚠️  IMPORTANT : 
echo    - Suis les instructions de l'installateur
echo    - C'est gratuit, pas besoin de compte
echo    - Une fois installé, lance Obsidian
echo    - Clique sur "Open folder as vault"
echo    - Sélectionne : %CD%
echo.
pause

REM Lancer l'installateur
start "" "%INSTALLER%"

echo.
echo ✅ Installateur lancé !
echo.
echo 📝 PROCHAINES ÉTAPES :
echo.
echo 1. Suis l'installation (Next, Next, Install)
echo 2. Lance Obsidian depuis le menu Démarrer
echo 3. Clique sur "Open folder as vault"
echo 4. Sélectionne ce dossier : %CD%
echo 5. Clique sur "Open"
echo.
echo 🎉 C'est fait ! Obsidian va ouvrir ton projet Temple IAM !
echo.
pause

