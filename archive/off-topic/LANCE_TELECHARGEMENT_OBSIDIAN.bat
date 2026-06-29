@echo off
chcp 65001 >nul
echo ========================================
echo 📥 TÉLÉCHARGEMENT OBSIDIAN
echo ========================================
echo.
echo Ouverture du site de téléchargement...
echo.
start https://obsidian.md/download
echo.
echo ✅ Site web ouvert !
echo.
echo 📝 INSTRUCTIONS :
echo.
echo 1. Sur le site, clique sur "Download for Windows"
echo 2. Le fichier va se télécharger dans ton dossier Téléchargements
echo 3. Une fois téléchargé, double-clique sur "Obsidian-Setup.exe"
echo 4. Suis l'installation (Next, Next, Install)
echo 5. Lance Obsidian depuis le menu Démarrer
echo 6. Clique sur "Open folder as vault"
echo 7. Sélectionne ce dossier : %CD%
echo 8. Clique sur "Open"
echo.
echo 🎉 C'est fait ! Obsidian va ouvrir ton projet Temple IAM !
echo.
pause

