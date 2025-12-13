#!/bin/bash
# 🎮 TEMPLE IAM GPU AGENTS - ENTRYPOINT SCRIPT 🏛️
# Script de démarrage pour conteneur GPU
#
# PLUS ULTRA ! DATTEBAYO ! 🚀⚡

set -e

echo "🏛️ TEMPLE IAM GPU AGENTS - DÉMARRAGE"
echo "======================================"

# Vérification GPU NVIDIA
echo "🔍 Vérification GPU NVIDIA..."
if nvidia-smi &> /dev/null; then
    echo "✅ GPU NVIDIA détecté !"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
else
    echo "❌ ERREUR: GPU NVIDIA non détecté !"
    echo "⚠️  Vérifiez que nvidia-docker2 est installé et configuré"
    exit 1
fi

# Vérification CUDA
echo ""
echo "🔍 Vérification CUDA..."
if command -v nvcc &> /dev/null; then
    echo "✅ CUDA disponible: $(nvcc --version | grep release | awk '{print $5}' | sed 's/,//')"
else
    echo "⚠️  CUDA nvcc non trouvé (normal pour runtime-only)"
fi

# Vérification Python
echo ""
echo "🔍 Vérification Python..."
python3 --version
echo "✅ Python OK"

# Vérification dépendances GPU
echo ""
echo "🔍 Vérification dépendances GPU..."
python3 -c "import gputil; print('✅ GPUtil OK')" || echo "⚠️  GPUtil non disponible"
python3 -c "import psutil; print('✅ psutil OK')" || echo "⚠️  psutil non disponible"
python3 -c "import numpy; print('✅ NumPy OK')" || echo "⚠️  NumPy non disponible"

# Création des répertoires nécessaires
echo ""
echo "📁 Création des répertoires..."
mkdir -p /temple-iam/logs
mkdir -p /temple-iam/results
mkdir -p /temple-iam/config
echo "✅ Répertoires créés"

# Affichage des informations GPU détaillées
echo ""
echo "🖥️  INFORMATIONS GPU:"
echo "===================="
nvidia-smi --query-gpu=index,name,driver_version,memory.total,memory.free,temperature.gpu,power.draw,power.limit --format=csv

# Affichage de la configuration
echo ""
echo "⚙️  CONFIGURATION:"
echo "================="
echo "Game: ${GAME_NAME:-Auto-detect}"
echo "Monitor Interval: ${MONITOR_INTERVAL:-1.0}s"
echo "Target Temp: ${TARGET_TEMP:-75}°C"
echo "Critical Temp: ${CRITICAL_TEMP:-85}°C"
echo "Log Level: ${LOG_LEVEL:-INFO}"

echo ""
echo "🚀 DÉMARRAGE DES AGENTS GPU..."
echo "======================================"
echo ""

# Exécution de la commande passée en argument
exec "$@"
