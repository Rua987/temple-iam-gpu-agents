# 🧠 ML Features - Apprentissage Intelligent GPU

## 🎯 Qu'est-ce que c'est ?

Le système de **Machine Learning** intégré au GPU Monitor permet d'apprendre automatiquement les patterns de vos jeux et d'optimiser les performances au fil du temps !

## ✨ Fonctionnalités

### 📊 **Apprentissage Automatique**
- **Pattern Learning** : Le système apprend comment chaque jeu se comporte thermiquement
- **Spike Detection** : Détecte automatiquement les pics de charge GPU
- **Trend Analysis** : Analyse les tendances thermiques en temps réel
- **Predictive Alerts** : Prédit la température future pour anticiper les problèmes

### 🎮 **Profils par Jeu**
Chaque jeu développe son propre profil basé sur vos sessions :
- **Thermal Profile** : Température moyenne, max, min et plages typiques
- **Performance Profile** : Charge GPU moyenne et FPS estimés
- **Stability Metrics** : Nombre de spikes et stabilité générale

### 🔮 **Insights en Temps Réel**
Pendant que vous jouez, le système affiche :
- **Tendance thermique** : 📈 Montée, 📉 Descente, ➡️ Stable
- **Prédiction +60s** : Température prédite dans 60 secondes
- **Stats de session** : Durée, nombre de datapoints, spikes détectés

## 🚀 Utilisation

### 1. **Monitoring Normal**

Lancez simplement le moniteur comme d'habitude :

```bash
python run_universal_monitor_v2.py
```

Le système ML est **automatiquement activé** ! Il collecte des données en arrière-plan.

### 2. **Analyser les Profils Appris**

Après quelques sessions de jeu, analysez les données :

```bash
python analyze_ml_profiles.py
```

Menu disponible :
- **Option 1** : Analyser un jeu spécifique
- **Option 2** : Comparer tous les jeux
- **Option 3** : Afficher le résumé

### 3. **Exemple d'Analyse**

```
================================================================================
📊 ANALYSE ML - CYBERPUNK 2077
================================================================================

📈 STATISTIQUES GÉNÉRALES:
  Sessions jouées:  5
  Temps total:      187.3 minutes (3.1h)

🌡️  PROFIL THERMIQUE:
  Température moyenne:  75.2°C
  Température max:      85.0°C
  Température min:      65.0°C
  Plage typique:        72-78°C
  Classification:       🟡 CHAUD (Acceptable)

⚡ PROFIL PERFORMANCE:
  GPU Load moyen:  92.3%
  FPS moyen:       58.4
  Classification:  🔴 SATURÉ (GPU à fond)

🎯 STABILITÉ:
  Spikes GPU totaux:  12
  Spikes par heure:   3.8
  Classification:     🟡 BON (Quelques variations)

💡 RECOMMANDATIONS INTELLIGENTES:
  1. 🌡️  Température élevée : Augmenter ventilation ou undervolt
  2. ⚡ GPU saturé : Réduire qualité graphique ou activer DLSS
```

## 📂 Structure des Données

Les données ML sont stockées dans `gpu_ml_data/` :

```
gpu_ml_data/
├── Cyberpunk_2077_20251216_013955.jsonl
├── Elden_Ring_20251216_143022.jsonl
└── Alan_Wake_2_20251216_183145.jsonl
```

Chaque fichier contient :
- **Métriques GPU** : Température, utilisation, VRAM, FPS
- **Métriques système** : CPU, RAM
- **Événements** : Spikes détectés, alertes
- **Métadonnées** : Timestamps, durée de session

## 🎯 Ce que le Système Apprend

### **Pattern 1 : Thermal Ramp-Up Curve**
Le système apprend combien de temps met chaque jeu pour atteindre sa température stable.

**Exemple** :
- Cyberpunk 2077 : 15 minutes pour stabiliser à 75°C
- Elden Ring : 8 minutes pour stabiliser à 63°C

### **Pattern 2 : Scene Spikes**
Détecte quelles zones/situations font exploser la charge GPU.

**Exemple** :
- Downtown Night City dans Cyberpunk : +15% charge GPU
- Boss fights dans Elden Ring : +25% charge GPU

### **Pattern 3 : FPS Sweet Spots**
Identifie la température optimale pour les meilleurs FPS.

**Exemple** :
- 65-68°C : 62 FPS ✅ (Sweet spot!)
- 77-80°C : 48 FPS ⚠️ (Thermal throttling)

### **Pattern 4 : Session Duration Effects**
Analyse comment les performances évoluent avec la durée de jeu.

**Exemple** :
- 0-30 min : 62 FPS à 68°C
- 90+ min : 54 FPS à 78°C (Thermal soak)

## 🔧 Configuration Avancée

### Désactiver le ML Logging

Si vous ne voulez pas collecter de données ML, modifiez `universal_gpu_monitor.py` :

```python
# Ligne 53 - Désactiver ML
self.ml_logger = None  # Au lieu de ML_LOGGER
```

### Changer le Dossier de Données

Dans `gpu_ml_logger.py` :

```python
# Ligne par défaut
ML_LOGGER = GPUMLLogger(log_directory="gpu_ml_data")

# Personnalisé
ML_LOGGER = GPUMLLogger(log_directory="/chemin/vers/mes/donnees")
```

## 📊 Comparaison de Jeux

Comparez facilement tous vos jeux :

```bash
python analyze_ml_profiles.py
# Choisir option 2
```

Exemple de sortie :

```
================================================================================
📊 COMPARAISON DES JEUX
================================================================================

Jeu                            Temp Moy     GPU Load     FPS        Spikes/h
--------------------------------------------------------------------------------
Alan Wake 2                      72.4°C       88.2%      57.3          4.2
Cyberpunk 2077                   75.2°C       92.3%      58.4          3.8
Elden Ring                       63.5°C       68.7%      59.8          1.5

🏆 CLASSEMENTS:
  🔥 Plus chaud:     Cyberpunk 2077 (75.2°C)
  ❄️  Plus frais:     Elden Ring (63.5°C)
  ⚡ Plus intensif:  Cyberpunk 2077 (92.3% GPU)
  🎯 Plus stable:    Elden Ring (1.5 spikes/h)
```

## 🤖 Prédictions en Temps Réel

Le système prédit la température future basée sur les tendances :

```
🧠 ML INSIGHTS - APPRENTISSAGE INTELLIGENT
--------------------------------------------------------------------------------
Tendance temp: 📈 MONTÉE
Préd. +60s:   78.2°C (+3.2°C)  ⚠️  Alerte : Va chauffer !
Session:      45.3 min | 2718 points
⚠️  Spikes GPU:   3 détecté(s)
```

## 💡 Astuces

1. **Jouez plusieurs sessions** du même jeu pour des profils plus précis
2. **Analysez régulièrement** les données pour voir l'évolution
3. **Comparez les jeux** pour identifier lesquels sont les plus exigeants
4. **Suivez les recommandations** pour optimiser vos paramètres

## 🏆 Bénéfices

✅ **Optimisation automatique** : Le système s'améliore à chaque session
✅ **Prévention des problèmes** : Prédictions et alertes précoces
✅ **Insights détaillés** : Comprenez vraiment comment vos jeux se comportent
✅ **Comparaisons faciles** : Identifiez vos jeux les plus gourmands
✅ **Recommandations personnalisées** : Basées sur VOS données réelles

## 🚀 Prochaines Étapes

Le système ML continuera d'évoluer avec :
- **Optimisation automatique** : Ajustement automatique fan/power limit
- **Détection de zones problématiques** : Identification GPS des zones chaudes
- **Apprentissage horaire** : Adaptation selon température ambiante
- **Profils saisonniers** : Ajustements été vs hiver

---

**IKUZO ! PLUS ULTRA ! 🔥🏛️⚡**

Votre GPU devient plus intelligent à chaque session ! 🧠🎮
