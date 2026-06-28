#!/bin/bash
# Script de démarrage propre - Force le rechargement complet

echo "🧹 Nettoyage cache Python..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

echo "✅ Cache nettoyé"
echo ""
echo "🚀 Lancement du moniteur GPU..."
echo ""

# Lance Python dans un sous-shell isolé
exec python3 run_universal_monitor_v2.py
