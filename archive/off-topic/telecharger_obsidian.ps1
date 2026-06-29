# Script de telechargement Obsidian
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TELECHARGEMENT OBSIDIAN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# URL de telechargement (derniere version)
$url = "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.7.3/Obsidian-Setup-1.7.3.exe"

# Dossier de telechargement
$downloadPath = Join-Path $env:USERPROFILE "Downloads"
$outputFile = Join-Path $downloadPath "Obsidian-Setup.exe"

Write-Host "Telechargement en cours..." -ForegroundColor Yellow
Write-Host "URL: $url" -ForegroundColor Gray
Write-Host "Destination: $outputFile" -ForegroundColor Gray
Write-Host ""

try {
    # Telecharger
    Invoke-WebRequest -Uri $url -OutFile $outputFile -UseBasicParsing
    
    Write-Host "Telechargement termine !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Fichier telecharge: $outputFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Lancement de l installateur..." -ForegroundColor Yellow
    Write-Host ""
    
    # Lancer l installateur
    Start-Process -FilePath $outputFile
    
    Write-Host "Installateur lance !" -ForegroundColor Green
    Write-Host ""
    Write-Host "PROCHAINES ETAPES:" -ForegroundColor Cyan
    Write-Host "   1. Suis l installation (Next, Next, Install)" -ForegroundColor White
    Write-Host "   2. Une fois installe, lance Obsidian" -ForegroundColor White
    Write-Host "   3. Clique sur Open folder as vault" -ForegroundColor White
    Write-Host "   4. Selectionne: C:\Users\admin\temple-iam-gpu-agents" -ForegroundColor White
    Write-Host "   5. Clique sur Open" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "Erreur lors du telechargement:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Telechargement manuel:" -ForegroundColor Yellow
    Write-Host "   Va sur: https://obsidian.md/download" -ForegroundColor White
    Write-Host "   Clique sur Download for Windows" -ForegroundColor White
}

Write-Host ""
Write-Host "Appuie sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
