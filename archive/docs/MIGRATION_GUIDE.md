# 🔄 Guide de Migration - Système Universel

## 📋 Vue d'ensemble

Temple IAM GPU Agents a été **entièrement refactorisé** pour supporter la **détection automatique de N'IMPORTE QUEL JEU** au lieu d'être limité à Alan Wake 2.

### 🎯 Nouveautés v2.0

- ✅ **Détection Universelle** : Reconnaît automatiquement n'importe quel jeu
- ✅ **Base de Données** : 20+ jeux AAA pré-configurés avec profils d'optimisation
- ✅ **Auto-Apprentissage** : Ajoute automatiquement les jeux inconnus
- ✅ **Profils Adaptatifs** : Optimisations thermiques spécifiques par jeu
- ✅ **Rétrocompatibilité** : Les anciens scripts fonctionnent toujours

---

## 🆕 Nouveaux Fichiers

### Core System
| Fichier | Description |
|---------|-------------|
| `games_database.py` | Base de données de 20+ jeux avec profils complets |
| `universal_game_detector.py` | Détecteur intelligent multi-jeux avec auto-apprentissage |
| `universal_gpu_monitor.py` | Moniteur GPU universel pour tous les jeux |
| `test_universal_system.py` | Script de test complet du nouveau système |

### Fichiers Modifiés
| Fichier | Changements |
|---------|-------------|
| `temple_iam_thermal_optimizer.py` | Refactorisé pour détection universelle |
| `docker-compose.gpu.yml` | Ajout service `universal-gpu-monitor` |

### Fichiers Conservés (Legacy)
| Fichier | Statut |
|---------|--------|
| `alan_wake2_gpu_monitor.py` | ✅ Conservé pour rétrocompatibilité |
| `temple_iam_alan_wake2_gpu_virtual_integration.py` | ✅ Conservé tel quel |

---

## 🚀 Migration Rapide

### Option 1 : Utiliser le Nouveau Système (Recommandé)

#### Python Direct
```bash
# Ancien (Alan Wake 2 uniquement)
python alan_wake2_gpu_monitor.py

# Nouveau (Tous les jeux)
python universal_gpu_monitor.py
```

#### Docker
```bash
# Ancien
docker-compose -f docker-compose.gpu.yml up gpu-monitor

# Nouveau (Universel)
docker-compose -f docker-compose.gpu.yml up universal-gpu-monitor

# Legacy (Alan Wake 2 uniquement)
docker-compose -f docker-compose.gpu.yml --profile legacy up legacy-gpu-monitor
```

### Option 2 : Garder l'Ancien Système

Rien à faire ! Les anciens fichiers continuent de fonctionner.

---

## 📊 Comparaison Ancien vs Nouveau

### Ancien Système (v1.0)
```python
# Limité à Alan Wake 2
alan_wake2_detected = _is_alan_wake2_running()
if alan_wake2_detected:
    print("Alan Wake 2 détecté")
```

**Limitations:**
- ❌ Un seul jeu supporté
- ❌ Pas de profils d'optimisation
- ❌ Configuration manuelle requise

### Nouveau Système (v2.0)
```python
# Détecte automatiquement TOUS les jeux
detected_games = game_detector.detect_running_games()
primary_game = game_detector.get_primary_game()

if primary_game:
    profile = game_detector.get_game_optimization_profile(primary_game)
    print(f"Jeu détecté: {primary_game.custom_name}")
    print(f"Profil: {profile['thermal_profile']}")
```

**Avantages:**
- ✅ Détection automatique multi-jeux
- ✅ Base de données de 20+ jeux
- ✅ Profils d'optimisation par jeu
- ✅ Auto-apprentissage des jeux inconnus

---

## 🎮 Jeux Supportés Nativement

Le système reconnaît automatiquement ces jeux avec profils optimisés :

### AAA Games
- ✅ Alan Wake 2
- ✅ Cyberpunk 2077
- ✅ Elden Ring
- ✅ Hogwarts Legacy
- ✅ Red Dead Redemption 2
- ✅ Starfield
- ✅ Call of Duty: Modern Warfare III
- ✅ Assassin's Creed Mirage
- ✅ Marvel's Spider-Man Remastered
- ✅ God of War
- ✅ The Last of Us Part I

### Competitive/Esports
- ✅ VALORANT
- ✅ Apex Legends
- ✅ Call of Duty: Warzone

### Racing/Simulation
- ✅ Forza Horizon 5

### Jeux Inconnus
- 🆕 **Auto-apprentissage** : Le système apprend automatiquement les nouveaux jeux

---

## 🔧 Configuration

### Variables d'Environnement

#### Ancien (v1.0)
```bash
GAME_NAME=AlanWake2  # Obligatoire
MONITOR_INTERVAL=1.0
```

#### Nouveau (v2.0)
```bash
# Plus de GAME_NAME nécessaire !
MONITOR_INTERVAL=1.0
AUTO_LEARN=true  # Active l'apprentissage automatique
LOG_LEVEL=INFO
```

### Fichier de Configuration

Le système crée automatiquement `learned_games.json` pour stocker les jeux appris :

```json
{
  "MyGame.exe": {
    "custom_name": "My Game",
    "first_detected": "2024-01-15T10:30:00",
    "detection_count": 5,
    "exe_path": "C:\\Games\\MyGame\\MyGame.exe"
  }
}
```

---

## 🧪 Tester le Nouveau Système

### Script de Test Complet
```bash
python test_universal_system.py
```

Ce script teste :
1. ✅ Base de données de jeux
2. ✅ Détecteur universel
3. ✅ Profils d'optimisation
4. ✅ Intégration GPU Monitor
5. ✅ Intégration Thermal Optimizer

### Test Manuel

#### 1. Test Détection
```python
from universal_game_detector import GAME_DETECTOR

# Détection automatique
games = GAME_DETECTOR.detect_running_games()
for game in games:
    print(f"Détecté: {game.custom_name} ({game.process_name})")
```

#### 2. Test Base de Données
```python
from games_database import GAMES_DB

# Recherche par nom
game = GAMES_DB.get_game_by_name("cyberpunk_2077")
print(f"Profil: {game.thermal_profile}")
print(f"Temp cible: {game.default_settings['target_temp']}°C")
```

#### 3. Test Moniteur
```python
from universal_gpu_monitor import UniversalGPUMonitor

monitor = UniversalGPUMonitor()
monitor.start_monitoring()  # Ctrl+C pour arrêter
```

---

## 🐳 Migration Docker

### Ancienne Configuration
```yaml
services:
  gpu-monitor:
    command: python3 alan_wake2_gpu_monitor.py
    environment:
      - GAME_NAME=AlanWake2
```

### Nouvelle Configuration
```yaml
services:
  universal-gpu-monitor:
    command: python3 universal_gpu_monitor.py
    environment:
      - AUTO_LEARN=true
    volumes:
      - ./learned_games.json:/temple-iam/learned_games.json
```

### Lancement
```bash
# Nouveau système universel
docker-compose -f docker-compose.gpu.yml up universal-gpu-monitor

# Thermal Optimizer (mis à jour automatiquement)
docker-compose -f docker-compose.gpu.yml up thermal-optimizer

# Tout en même temps
docker-compose -f docker-compose.gpu.yml up
```

---

## ⚠️ Points d'Attention

### 1. Dépendances
Les nouveaux modules nécessitent les mêmes dépendances que l'ancien système :
```bash
pip install -r requirements_gpu.txt
```

### 2. Permissions
Le système a besoin d'accès aux processus pour détecter les jeux :
- **Windows** : Exécuter en tant qu'administrateur si nécessaire
- **Linux** : Permissions sudo pour certains processus

### 3. Performance
- Auto-apprentissage peut ralégir légèrement la détection initiale
- Désactivez avec `AUTO_LEARN=false` si besoin

### 4. Jeux Appris
Le fichier `learned_games.json` grandit avec le temps. Nettoyez-le périodiquement :
```bash
# Backup
cp learned_games.json learned_games.backup.json

# Réinitialiser
echo "{}" > learned_games.json
```

---

## 🔄 Rollback (Retour Arrière)

Si vous rencontrez des problèmes :

### Python
```bash
# Retour à l'ancien moniteur
python alan_wake2_gpu_monitor.py
```

### Docker
```bash
# Utiliser le profil legacy
docker-compose -f docker-compose.gpu.yml --profile legacy up
```

---

## 📚 Documentation Complémentaire

- **Guide Utilisateur** : `GUIDE_UTILISATEUR_SIMPLE.md`
- **Quick Start** : `QUICK_START.md`
- **Docker Guide** : `README-DOCKER.md`
- **README Principal** : `README.md`

---

## 🆘 Support

### Problèmes Courants

#### "Module 'games_database' not found"
```bash
# Vérifier que vous êtes dans le bon répertoire
ls games_database.py universal_game_detector.py

# Réinstaller les dépendances
pip install -r requirements_gpu.txt
```

#### "Aucun jeu détecté"
```bash
# Tester manuellement
python test_universal_system.py

# Vérifier les processus
python -c "from universal_game_detector import GAME_DETECTOR; print(GAME_DETECTOR.detect_running_games())"
```

#### "GPU non disponible"
```bash
# Vérifier NVIDIA
nvidia-smi

# Vérifier GPUtil
python -c "import GPUtil; print(GPUtil.getGPUs())"
```

---

## 🎉 Conclusion

Le nouveau système universel offre :
- ✅ **Simplicité** : Plus besoin de configuration manuelle
- ✅ **Flexibilité** : Supporte n'importe quel jeu
- ✅ **Intelligence** : Apprentissage automatique
- ✅ **Performance** : Optimisations par profil de jeu

**Recommandation** : Migrez vers le nouveau système pour profiter de toutes les fonctionnalités !

---

**PLUS ULTRA ! DATTEBAYO !** 🚀⚡🏛️
